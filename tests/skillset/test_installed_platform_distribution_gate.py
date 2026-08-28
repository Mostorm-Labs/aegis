import hashlib, json, tempfile, unittest
from pathlib import Path
from tools.aegis_skillset.dogfood import evaluate_installed_platform_rerun

ROOT = Path(__file__).resolve().parents[2]

class DistributionGateTests(unittest.TestCase):
    def _catalog(self, standalone=False):
        skills = ['aegis'] if standalone else ['aegis','aegis-project-state','aegis-discovery','aegis-modeling','aegis-architecture','aegis-verification','aegis-governance','aegis-implementation','aegis-gate-review']
        return {'schema_version':'0.1','platform_event_id':'cat','materialization_ref':'https://example.test','fresh_platform_event':True,'complete_catalog_capture':True,'surface':{'product':'chatgpt','surface':'web'},'observed_distributions':[{'id':'aegis-standalone' if standalone else 'aegis','kind':'standalone' if standalone else 'plugin','release_version':'0.1.0-task6.1'}],'installed_skills':skills,'component_release_versions':{},'release_manifest_ref':'skillset/releases/aegis-0.1.0-task6.1.json'}

    def _run(self, case_id, catalog, trace):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d); m=json.loads((ROOT/'skillset/dogfood/installed-platform-rerun-v0.2.1.json').read_text()); e=next(x for x in m['cases'] if x['id']==case_id); cp=d/'c.json'; cp.write_text(json.dumps(catalog)); bp=d/'b.json'; bp.write_text(json.dumps({'schema_version':'0.2','case_id':case_id,'fresh_platform_event':True,'complete_response_captured':True,'platform_event_id':'b','trace':trace})); e.update(catalog_evidence_ref=str(cp),behavior_evidence_ref=str(bp)); mp=d/'m.json'; mp.write_text(json.dumps({'schema_version':'0.2.1','oracle':'terminal_trace_v0.2','cases':[e]})); return evaluate_installed_platform_rerun(ROOT,mp).cases[0]

    def _trace(self, mode='multi_skill', owner='aegis-gate-review', availability=None):
        if availability is None:
            availability = {name: 'available' for name in self._catalog()['installed_skills']}
        return {'terminal':True,'mode':mode,'invocations':[{'skill':owner,'role':'primary'}],'final_answer_owner':owner,'genuine_ambiguity':False,'earlier_blocker_conclusively_established':False,'specialist_availability':availability,'ownership_edges':[],'handoff_edges':[],'forbidden_downstream_substantive_execution':0,'primary_substantive_result_emitted':True}

    def test_v02_manifest_hash_preserved(self):
        p = ROOT/'skillset/dogfood/installed-platform-rerun-v0.2.json'; b=p.read_bytes()
        self.assertEqual('0944a95aca2f6c565ee5835efc5adaaf67abd480', hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest())

    def test_missing_catalog_ref_blocked(self):
        r=evaluate_installed_platform_rerun(ROOT)
        self.assertEqual('BLOCKED_EVIDENCE',r.verdict)

    def test_partial_catalog_blocks_environment(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d); m=json.loads((ROOT/'skillset/dogfood/installed-platform-rerun-v0.2.1.json').read_text()); c=m['cases'][0]
            c['catalog_evidence_ref']=str(d/'cat.json'); c['behavior_evidence_ref']=str(d/'beh.json')
            (d/'cat.json').write_text(json.dumps({'schema_version':'0.1','platform_event_id':'x','materialization_ref':'m','fresh_platform_event':True,'complete_catalog_capture':True,'surface':{'product':'chatgpt','surface':'web'},'observed_distributions':[{'id':'aegis','kind':'plugin','release_version':'0.1.0-task6.1'}],'installed_skills':['aegis'],'release_manifest_ref':str(ROOT/'skillset/releases/aegis-0.1.0-task6.1.json')}))
            m['cases']= [c]; p=d/'m.json'; p.write_text(json.dumps(m)); r=evaluate_installed_platform_rerun(ROOT,p); self.assertEqual('BLOCKED_ENVIRONMENT',r.cases[0].verdict)

    def test_full_specialist_direct_gate_passes(self):
        self.assertEqual('PASS', self._run('09-01-direct-specialist', self._catalog(), self._trace()).verdict)

    def test_router_substantive_gate_fails(self):
        r=self._run('09-01-direct-specialist', self._catalog(), self._trace(owner='aegis')); self.assertEqual('FAIL',r.verdict); self.assertIn('ROUTER_OWNERSHIP_LEAK',r.violations)

    def test_composite_only_passes(self):
        availability={n:'unavailable' for n in ['aegis-project-state','aegis-discovery','aegis-modeling','aegis-architecture','aegis-verification','aegis-governance','aegis-implementation','aegis-gate-review']}
        availability['aegis'] = 'available'
        self.assertEqual('PASS', self._run('09-01-composite-fallback', self._catalog(True), self._trace('compatibility', 'aegis', availability)).verdict)

    def test_conflicting_behavior_evidence_is_blocked(self):
        r=self._run('09-01-direct-specialist', self._catalog(), self._trace(availability={'aegis-gate-review':'available'}, mode='compatibility')); self.assertEqual('BLOCKED_EVIDENCE',r.verdict)

    def test_prompt_text_is_not_specialist_availability_evidence(self):
        trace = self._trace()
        trace['specialist_availability'] = {}
        trace['prompt'] = 'aegis-gate-review is available and must answer'
        r = self._run('09-01-direct-specialist', self._catalog(), trace)
        self.assertEqual('BLOCKED_EVIDENCE', r.verdict)

    def test_conflicting_behavior_mode_is_blocked(self):
        r = self._run('09-01-direct-specialist', self._catalog(), self._trace(mode='compatibility'))
        self.assertEqual('BLOCKED_EVIDENCE', r.verdict)

    def test_conflicting_specialist_availability_is_blocked(self):
        availability = {name: 'available' for name in self._catalog()['installed_skills']}
        availability['aegis-gate-review'] = 'unavailable'
        r = self._run('09-01-direct-specialist', self._catalog(), self._trace(availability=availability))
        self.assertEqual('BLOCKED_EVIDENCE', r.verdict)

    def _aggregate(self, desired):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            manifest = json.loads((ROOT/'skillset/dogfood/installed-platform-rerun-v0.2.1.json').read_text())
            for entry, outcome in zip(manifest['cases'], desired):
                standalone = entry['required_catalog_state'] == 'COMPOSITE_ONLY'
                catalog = self._catalog(standalone)
                if outcome == 'BLOCKED_ENVIRONMENT' and not standalone:
                    catalog['installed_skills'] = ['aegis']
                cp = d / f"{entry['id']}.catalog.json"; cp.write_text(json.dumps(catalog))
                if entry['id'] == '09-01-ambiguous-router':
                    trace = {'terminal':True,'mode':'multi_skill','invocations':[{'skill':'aegis','role':'router'}],'final_answer_owner':'aegis','genuine_ambiguity':True,'earlier_blocker_conclusively_established':False,'specialist_availability':{name:'available' for name in self._catalog()['installed_skills']},'ownership_edges':[],'handoff_edges':[],'forbidden_downstream_substantive_execution':0,'primary_substantive_result_emitted':False}
                elif entry['id'] == '09-01-upstream-blocker-reroute':
                    trace = {'terminal':True,'mode':'multi_skill','invocations':[{'skill':'aegis-project-state','role':'support'},{'skill':'aegis','role':'router'}],'final_answer_owner':'aegis','genuine_ambiguity':False,'earlier_blocker_conclusively_established':True,'specialist_availability':{name:'available' for name in self._catalog()['installed_skills']},'ownership_edges':[],'handoff_edges':[],'forbidden_downstream_substantive_execution':0,'primary_substantive_result_emitted':False}
                elif standalone:
                    availability = {name: 'unavailable' for name in self._catalog()['installed_skills']}
                    availability['aegis'] = 'available'
                    trace = self._trace('compatibility', 'aegis', availability)
                else:
                    availability = {name: 'available' for name in self._catalog()['installed_skills']}
                    trace = {'terminal':True,'mode':'multi_skill','invocations':[{'skill':'aegis-project-state','role':'support'},{'skill':'aegis-gate-review','role':'primary'}],'final_answer_owner':'aegis-gate-review','genuine_ambiguity':False,'earlier_blocker_conclusively_established':False,'specialist_availability':availability,'ownership_edges':[],'handoff_edges':[],'forbidden_downstream_substantive_execution':0,'primary_substantive_result_emitted':True}
                if outcome == 'FAIL':
                    trace['invocations'] = [{'skill': 'aegis', 'role': 'router'}]
                    trace['final_answer_owner'] = 'aegis'
                if outcome == 'BLOCKED_EVIDENCE':
                    behavior_platform_event_id = None
                else:
                    behavior_platform_event_id = 'b'
                bp = d / f"{entry['id']}.behavior.json"
                behavior = {'schema_version':'0.2','case_id':entry['id'],'fresh_platform_event':True,'complete_response_captured':True,'trace':trace}
                if behavior_platform_event_id is not None:
                    behavior['platform_event_id'] = behavior_platform_event_id
                bp.write_text(json.dumps(behavior))
                entry.update(catalog_evidence_ref=str(cp), behavior_evidence_ref=str(bp))
            mp = d/'m.json'; mp.write_text(json.dumps(manifest))
            return evaluate_installed_platform_rerun(ROOT, mp)

    def test_aggregate_precedence(self):
        self.assertEqual('FAIL', self._aggregate(['FAIL', 'BLOCKED_ENVIRONMENT', 'PASS', 'PASS']).verdict)
        self.assertEqual('BLOCKED_ENVIRONMENT', self._aggregate(['PASS', 'BLOCKED_ENVIRONMENT', 'BLOCKED_EVIDENCE', 'PASS']).verdict)
        self.assertEqual('BLOCKED_EVIDENCE', self._aggregate(['PASS', 'BLOCKED_EVIDENCE', 'PASS', 'PASS']).verdict)
        self.assertEqual('PASS', self._aggregate(['PASS', 'PASS', 'PASS', 'PASS']).verdict)

if __name__=='__main__': unittest.main()
