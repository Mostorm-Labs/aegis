from __future__ import annotations
from copy import deepcopy
from tools.aegis_control.canonical import canonical_digest

ANCHOR = 'a996edb00fbbe1f292bba6e3634118e215fe4c14'
NOW = '2026-08-31T06:30:00Z'

EXPECTED_KEYS = {
    'active_occurrence_ref', 'predecessor_occurrence_ref', 'target_record_revision',
    'target_record_digest', 'trusted_basis_digest', 'package_ref', 'work_scope_ref'
}


def root_work_scope_ref(lane_id='lane_01', scope_id=None):
    return {
        'id_scheme': 'control-work-scope-v0.2',
        'id': scope_id or f'ws_{lane_id}',
        'child_work_binding': None,
    }


def expected_state(**overrides):
    value = {k: None for k in EXPECTED_KEYS}
    value.update(overrides)
    return value


def package_record(package_id='pkg_01', lane_id='lane_pkg', revision=1, scope_name='cp-i02'):
    return {
        'schema_version':'0.2','kind':'VERIFICATION_BOUND_IMPLEMENTATION_PACKAGE',
        'id_scheme':'verification-bound-package-v0.2','id':package_id,
        'record_revision':revision,'recorded_at':NOW,'extensions':{},
        'control_lane_id':lane_id,'work_scope_ref':root_work_scope_ref(lane_id),
        'trusted_basis':{'authority':['P13','P15','P16','P17','P20']},
        'scope':{'name':scope_name},'verification_binding':{'spec':'CPV-C01'},
        'policy_binding':{'control_autonomy':'REVIEW_GUARDED'},
        'task_anchor':{'revision':ANCHOR,'relation':'ancestor'},'package_digest':'sha256:' + '0'*64,
    }


def occurrence_record(occurrence_id='so_01', lane_id='lane_01'):
    return {
        'schema_version':'0.2','kind':'STAGE_OCCURRENCE','id_scheme':'stage-occurrence-v0.2',
        'id':occurrence_id,'record_revision':1,'recorded_at':NOW,'extensions':{},
        'control_lane_id':lane_id,'work_scope_ref':root_work_scope_ref(lane_id),
        'stage_span':{'stages':['P32']},'primary_owner':'aegis-implementation',
        'state':'OPEN','trusted_basis':{'authority':['P13','P15','P16','P17','P20']},
        'policy_binding':{'control_autonomy':'REVIEW_GUARDED'},
        'schedule_basis':{'reason_code':'IMPLEMENT','required_child_acceptance_bindings':[]},'input_refs':[],
        'repair_context':None,'execution_navigation':None,'terminal':None,
    }


def canonical_occurrence_ref(occurrence_id='so_01', lane_id='lane_01'):
    record = occurrence_record(occurrence_id, lane_id)
    digest = canonical_digest(record)
    return {
        'object_type':'STAGE_OCCURRENCE',
        'id':occurrence_id,
        'ref':f'control:STAGE_OCCURRENCE:{occurrence_id}@1',
        'identity':{'scheme':'sha256','value':digest},
    }


def escalation_record(escalation_id='esc_01', occurrence_id='so_01', lane_id='lane_01'):
    return {
        'schema_version':'0.2','kind':'ESCALATION','id_scheme':'escalation-v0.2',
        'id':escalation_id,'record_revision':1,'recorded_at':NOW,'extensions':{},
        'control_lane_id':lane_id,'work_scope_ref':root_work_scope_ref(lane_id),
        'raised_from_occurrence_ref':canonical_occurrence_ref(occurrence_id, lane_id),
        'trusted_basis_digest':canonical_digest({'authority':['P13','P15','P16','P17','P20']}),
        'category':'AUTHORITY_CONFLICT','owning_layer':'P21',
        'required_decision':{'decision_kind':'AUTHORITY_RECONCILIATION','summary':'resolve authority question'},
        'evidence_snapshot_refs':[],
    }


def terminal_facts(outcome='COMPLETED', status='READY', *, raised=None, finding_refs=None, earliest=None):
    return {
        'outcome_category': outcome,
        'status': status,
        'produced_refs': [],
        'finding_refs': list(finding_refs or []),
        'raised_escalation_ids': list(raised or []),
        'resolved_escalation_ids': [],
        'earliest_untrusted_layer': earliest,
        'navigation_result': None,
    }


def make_request(operation_name, request_id, lane_id, payload, expected=None):
    actor = {'class':'CONTROL_PLANE','id':'cp-i02-test'}
    exp = deepcopy(expected if expected is not None else expected_state())
    if exp.get('work_scope_ref') is None:
        source = payload.get('occurrence') or payload.get('package') or payload.get('escalation')
        if isinstance(source, dict) and source.get('work_scope_ref') is not None:
            exp['work_scope_ref'] = deepcopy(source['work_scope_ref'])
        else:
            exp['work_scope_ref'] = root_work_scope_ref(lane_id)
    semantic = {'operation_name':operation_name,'actor':actor,'control_lane_id':lane_id,'expected_state':exp,'payload':payload}
    return {
        **semantic,
        'operation_request_id':request_id,
        'idempotency_fingerprint':canonical_digest(semantic),
    }


def conflicting_request(request):
    out = deepcopy(request)
    out['payload'] = deepcopy(out['payload'])
    out['payload']['conflict_marker'] = True
    semantic = {k:out[k] for k in ('operation_name','actor','control_lane_id','expected_state','payload')}
    out['idempotency_fingerprint'] = canonical_digest(semantic)
    return out
