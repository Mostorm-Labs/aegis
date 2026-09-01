import tempfile
import threading
import unittest
from pathlib import Path

from tests.control_plane.cp_i02_fixtures import (
    conflicting_request, escalation_record, expected_state, make_request,
    occurrence_record, package_record, terminal_facts,
)
from tools.aegis_control.mutation import MutationRejected, MutationService
from tools.aegis_control.store import ControlStore

class MutationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / 'control.db')
        self.store = ControlStore(self.db)
        self.mutation = MutationService(self.store)
    def tearDown(self): self.tmp.cleanup()

    def test_package_materialize_revise_and_idempotency(self):
        req = make_request('MATERIALIZE_IMPLEMENTATION_PACKAGE','req_pkg_1','lane_pkg',{'package':package_record()})
        first = self.mutation.apply(req)
        self.assertEqual(first, self.mutation.apply(req))
        self.assertEqual(1, len(self.store.read_revisions('VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE','pkg_01')))
        current = self.store.read_latest('VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE','pkg_01')
        revised = package_record(revision=2, scope_name='cp-i02-r2')
        revreq = make_request('REVISE_IMPLEMENTATION_PACKAGE','req_pkg_2','lane_pkg',{'package':revised}, expected_state(target_record_revision=1,target_record_digest=current.digest))
        self.mutation.apply(revreq)
        duplicate = make_request('MATERIALIZE_IMPLEMENTATION_PACKAGE','req_pkg_duplicate','lane_pkg',{'package':package_record()})
        before_duplicate = self.store.snapshot_counts()
        with self.assertRaisesRegex(MutationRejected,'PACKAGE_IDENTITY_CONFLICT'):
            self.mutation.apply(duplicate)
        self.assertEqual(before_duplicate, self.store.snapshot_counts())
        lineage = self.store.read_revisions('VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE','pkg_01')
        self.assertEqual([1,2],[x.record['record_revision'] for x in lineage])
        stale = make_request('REVISE_IMPLEMENTATION_PACKAGE','req_pkg_stale','lane_pkg',{'package':package_record(revision=2,scope_name='stale')}, expected_state(target_record_revision=1,target_record_digest=current.digest))
        with self.assertRaisesRegex(MutationRejected,'STALE_PACKAGE_REVISION'):
            self.mutation.apply(stale)
        self.assertEqual(2,len(self.store.read_revisions('VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE','pkg_01')))
        with self.assertRaisesRegex(MutationRejected,'OPERATION_IDEMPOTENCY_CONFLICT'):
            self.mutation.apply(conflicting_request(req))
        self.assertEqual(2,len(self.store.read_revisions('VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE','pkg_01')))

    def test_schedule_atomic_shape_and_same_lane_race(self):
        req = make_request('SCHEDULE_STAGE_OCCURRENCE','req_sched_1','lane_01',{'occurrence':occurrence_record('so_01','lane_01')})
        result = self.mutation.apply(req)
        self.assertEqual('APPLIED', result['status'])
        self.assertEqual(1, self.store.read_lane_head('lane_01').version)
        self.assertEqual(1, len(self.store.read_outbox()))
        self.assertEqual(1, len(self.store.read_revisions('STAGE_OCCURRENCE','so_01')))

        race_db = str(Path(self.tmp.name) / 'race.db')
        ControlStore(race_db)
        barrier = threading.Barrier(2)
        outcomes=[]
        def run(index):
            svc = MutationService(ControlStore(race_db), before_transaction=lambda: barrier.wait())
            r = make_request('SCHEDULE_STAGE_OCCURRENCE',f'req_race_{index}','lane_race',{'occurrence':occurrence_record(f'so_race_{index}','lane_race')})
            try: outcomes.append(('ok',svc.apply(r)))
            except MutationRejected as exc: outcomes.append((exc.code,None))
        t1=threading.Thread(target=run,args=(1,)); t2=threading.Thread(target=run,args=(2,))
        t1.start(); t2.start(); t1.join(); t2.join()
        self.assertEqual(1,sum(1 for code,_ in outcomes if code=='ok'))
        self.assertEqual(1,sum(1 for code,_ in outcomes if code=='CONTROL_LANE_SCHEDULE_CONFLICT'))
        race_store=ControlStore(race_db)
        self.assertEqual(1,len(race_store.read_outbox()))
        self.assertEqual(1,sum(len(race_store.read_revisions('STAGE_OCCURRENCE',f'so_race_{i}')) for i in (1,2)))
        self.assertEqual(1, race_store.snapshot_counts()['idempotency'])

    def test_independent_lanes_both_commit(self):
        db = str(Path(self.tmp.name) / 'lanes.db')
        ControlStore(db)
        barrier=threading.Barrier(2); outcomes=[]
        def run(index):
            svc=MutationService(ControlStore(db), before_transaction=lambda: barrier.wait())
            r=make_request('SCHEDULE_STAGE_OCCURRENCE',f'req_lane_{index}',f'lane_{index}',{'occurrence':occurrence_record(f'so_lane_{index}',f'lane_{index}')})
            try: outcomes.append(svc.apply(r)['status'])
            except Exception as exc: outcomes.append(type(exc).__name__)
        ts=[threading.Thread(target=run,args=(i,)) for i in (1,2)]
        [t.start() for t in ts]; [t.join() for t in ts]
        self.assertEqual(['APPLIED','APPLIED'],sorted(outcomes))
        s=ControlStore(db); self.assertEqual(2,len(s.read_outbox()))
        self.assertEqual(2, s.snapshot_counts()['idempotency'])

    def test_terminal_and_escalation_boundaries(self):
        schedule=make_request('SCHEDULE_STAGE_OCCURRENCE','req_s','lane_01',{'occurrence':occurrence_record()})
        self.mutation.apply(schedule)
        open_row=self.store.read_latest('STAGE_OCCURRENCE','so_01')
        term=make_request('TERMINATE_STAGE_OCCURRENCE','req_t','lane_01',{'occurrence_id':'so_01','recorded_at':'2026-08-31T06:31:00Z','terminal':terminal_facts()},expected_state(target_record_revision=1,target_record_digest=open_row.digest))
        self.mutation.apply(term)
        self.assertEqual(2,len(self.store.read_revisions('STAGE_OCCURRENCE','so_01')))
        self.assertEqual(1,len(self.store.read_outbox()))
        with self.assertRaises(MutationRejected): self.mutation.apply(make_request('TERMINATE_STAGE_OCCURRENCE','req_t2','lane_01',term['payload'],term['expected_state']))

        esc_db=str(Path(self.tmp.name)/'esc.db'); esc_store=ControlStore(esc_db); esc_mut=MutationService(esc_store)
        esc_mut.apply(make_request('SCHEDULE_STAGE_OCCURRENCE','req_es','lane_01',{'occurrence':occurrence_record()}))
        current=esc_store.read_latest('STAGE_OCCURRENCE','so_01')
        esc=escalation_record()
        raise_req=make_request('RAISE_ESCALATION','req_e','lane_01',{'occurrence_id':'so_01','recorded_at':'2026-08-31T06:32:00Z','escalation':esc,'terminal':terminal_facts('ESCALATED','BLOCKED_UNRESOLVED_DECISION',raised=['esc_01'],earliest='P21')},expected_state(target_record_revision=1,target_record_digest=current.digest))
        esc_mut.apply(raise_req)
        self.assertEqual(1,len(esc_store.read_revisions('ESCALATION','esc_01')))
        self.assertEqual(2,len(esc_store.read_revisions('STAGE_OCCURRENCE','so_01')))
        self.assertEqual(['esc_01'],esc_store.read_latest('STAGE_OCCURRENCE','so_01').record['terminal']['raised_escalation_ids'])

    def test_unsupported_later_operation_is_zero_mutation(self):
        # RECORD_EXECUTION_PROGRESS is current CP-I05 behavior. Keep the original
        # CP-I02 invariant by probing an operation that is still a later slice.
        req=make_request('SCHEDULE_REPAIR_OCCURRENCE','req_u','lane_01',{'x':1})
        before=self.store.snapshot_counts()
        with self.assertRaisesRegex(MutationRejected,'UNSUPPORTED_OPERATION_IN_CP_I02'): self.mutation.apply(req)
        self.assertEqual(before,self.store.snapshot_counts())

if __name__=='__main__': unittest.main()
