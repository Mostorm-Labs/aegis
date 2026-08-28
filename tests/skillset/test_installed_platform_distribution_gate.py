import hashlib, json, tempfile, unittest
from pathlib import Path
from tools.aegis_skillset.dogfood import evaluate_installed_platform_rerun

ROOT = Path(__file__).resolve().parents[2]

class DistributionGateTests(unittest.TestCase):
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

if __name__=='__main__': unittest.main()
