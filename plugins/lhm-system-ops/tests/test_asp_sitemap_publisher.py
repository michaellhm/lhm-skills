import importlib.util, tempfile, unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; HELPER=ROOT/'assets/host/lhm-asp-sitemap-publisher'
spec=importlib.util.spec_from_loader('asp_publisher',SourceFileLoader('asp_publisher',str(HELPER)))
publisher=importlib.util.module_from_spec(spec); spec.loader.exec_module(publisher)

class AspPublisherTests(unittest.TestCase):
    def request(self,root,**updates):
        publisher.SOURCE_ROOT=root.parent
        sitemap=root/'australian-sports-physio/sitemap/index.html'; sitemap.parent.mkdir(parents=True); sitemap.write_text('<title>ASP sitemap</title>')
        value={'schema_version':1,'request_id':root.name,'repository':publisher.REPOSITORY,'branch':'main','expected_base_commit':'a'*40,'source_directory':str(root),'paths':['australian-sports-physio/sitemap/index.html'],'commit_message':'asp sitemap: publish validated package'}
        value.update(updates); return value
    def test_exact_allowlist(self):
        with tempfile.TemporaryDirectory() as temporary:
            good=self.request(Path(temporary)); publisher.validate(good)
            for update in ({'repository':'other/repo'},{'branch':'cto/test'},{'paths':['other-client/index.html']},{'paths':['../escape']}):
                with self.assertRaises(ValueError): publisher.validate({**good,**update})
    def test_rejects_commands_refspecs_and_forbidden_authority(self):
        with tempfile.TemporaryDirectory() as temporary:
            good=self.request(Path(temporary))
            for key in ('command','refspec','dns','client_contact','production_site'):
                with self.assertRaisesRegex(ValueError,'schema'): publisher.validate({**good,key:'forbidden'})
    def test_missing_root_credential_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            publisher.SSH_KEY=Path(temporary)/'missing'; publisher.KNOWN_HOSTS=Path(temporary)/'hosts'
            with self.assertRaisesRegex(ValueError,'credential is not configured'): publisher.ssh_env()

    def test_source_must_be_exact_request_staging_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'asp-001'; root.mkdir(); good=self.request(root)
            publisher.validate(good)
            elsewhere=Path(temporary)/'elsewhere'; elsewhere.mkdir()
            with self.assertRaisesRegex(ValueError,'source_directory'):
                publisher.validate({**good,'source_directory':str(elsewhere)})

if __name__=='__main__': unittest.main()
