import hashlib, importlib.util, json, tempfile, unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]; HELPER=ROOT/'assets/host/lhm-prototype-publisher'
spec=importlib.util.spec_from_loader('prototype_publisher',SourceFileLoader('prototype_publisher',str(HELPER)))
publisher=importlib.util.module_from_spec(spec); spec.loader.exec_module(publisher)

class PrototypePublisherTests(unittest.TestCase):
    def request(self,root,content=b'<title>ASP sitemap</title>',**updates):
        publisher.SOURCE_ROOT=root.parent
        path='australian-sports-physio/sitemap/index.html'; artifact=root/path
        artifact.parent.mkdir(parents=True); artifact.write_bytes(content)
        manifest=[{'path':path,'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content)}]
        value={'schema_version':1,'request_id':root.name,'repository':publisher.REPOSITORY,'branch':'main','expected_base_commit':'a'*40,'source_directory':str(root),'manifest':manifest,'package_manifest_sha256':hashlib.sha256(publisher.canonical_manifest(manifest)).hexdigest(),'commit_message':'prototype: publish ASP sitemap v2','workflow':publisher.WORKFLOW.copy()}
        value.update(updates); return value

    def test_authoritative_asp_package_is_accepted(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'asp-sitemap-v2-publish-20260820'; root.mkdir()
            request=self.request(root,b'x'*115238)
            request['manifest'][0]['sha256']='74b87dbc0f20c1d79326e11f342e1169d5777f17eded8683729f57b0d7650a70'
            # The authoritative digest is content-derived; use a mock because the source artifact is root-side.
            request['package_manifest_sha256']='b52a6de06e5e30a20b24e8e5b5a3c8c1703ffef04c93df2dde4d3026305f5115'
            with mock.patch.object(publisher,'file_digest',return_value=(115238,request['manifest'][0]['sha256'])):
                publisher.validate(request)

    def test_closed_schema_and_exact_route(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'request-001'; root.mkdir(); good=self.request(root)
            publisher.validate(good)
            for update in ({'repository':'other/repo'},{'branch':'cto/test'},{'workflow':{**publisher.WORKFLOW,'id':1}}):
                with self.assertRaises(ValueError): publisher.validate({**good,**update})
            for key in ('command','refspec','dns','client_contact','production_site','basicops_token'):
                with self.assertRaisesRegex(ValueError,'schema'): publisher.validate({**good,key:'forbidden'})

    def test_manifest_tamper_path_escape_duplicate_and_digest_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'request-001'; root.mkdir(); good=self.request(root)
            bad_entries=[
                [{'path':'../escape','sha256':'a'*64,'bytes':1}],
                good['manifest']*2,
                [{**good['manifest'][0],'bytes':good['manifest'][0]['bytes']+1}],
            ]
            for manifest in bad_entries:
                with self.assertRaises(ValueError): publisher.validate({**good,'manifest':manifest})
            with self.assertRaisesRegex(ValueError,'package manifest digest'):
                publisher.validate({**good,'package_manifest_sha256':'not-a-digest'})

    def test_source_must_be_exact_request_staging_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'request-001'; root.mkdir(); good=self.request(root)
            elsewhere=Path(temporary)/'elsewhere'; elsewhere.mkdir()
            with self.assertRaisesRegex(ValueError,'source_directory'): publisher.validate({**good,'source_directory':str(elsewhere)})

    def test_missing_root_credential_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            publisher.SSH_KEY=Path(temporary)/'missing'; publisher.KNOWN_HOSTS=Path(temporary)/'hosts'
            with self.assertRaisesRegex(ValueError,'credential is not configured'): publisher.ssh_env()

    def test_public_readback_requires_exact_bytes_and_hash(self):
        entry={'path':'client/homepage/index.html','bytes':4,'sha256':hashlib.sha256(b'good').hexdigest()}
        response=mock.MagicMock(); response.__enter__.return_value=response; response.status=200; response.read.return_value=b'evil'
        with mock.patch.object(publisher.urllib.request,'urlopen',return_value=response):
            with self.assertRaisesRegex(ValueError,'does not match'): publisher.verify_public(entry)

    def test_contract_schemas_are_closed(self):
        for name in ('prototype-publication.request.schema.json','prototype-publication.result.schema.json','prototype-basicops-handoff.schema.json','capability-restored.schema.json'):
            schema=json.loads((ROOT/'references'/name).read_text())
            self.assertIs(schema['additionalProperties'],False)

if __name__=='__main__': unittest.main()
