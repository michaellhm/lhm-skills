import hashlib, importlib.util, json, os, tempfile, unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]; HELPER=ROOT/'assets/host/lhm-prototype-publisher'
spec=importlib.util.spec_from_loader('prototype_publisher',SourceFileLoader('prototype_publisher',str(HELPER)))
publisher=importlib.util.module_from_spec(spec); spec.loader.exec_module(publisher)

class PrototypePublisherTests(unittest.TestCase):
    def request(self,root,client='alpha-health',kind='sitemap',files=None,**updates):
        publisher.SOURCE_ROOT=root.parent
        files=files or {'index.html':b'<title>Prototype</title>','styles/site.css':b'body{}','scripts/site.js':b'console.log("static")','data/site.json':b'{"ok":true}','images/logo.webp':b'RIFFimage','fonts/site.woff2':b'wOF2font'}
        manifest=[]
        for relative,data in files.items():
            path=root/client/kind/relative; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
            manifest.append({'path':f'{client}/{kind}/{relative}','sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
        manifest.sort(key=lambda x:x['path']); request_id=root.name
        index=next(item for item in manifest if item['path']==f'{client}/{kind}/index.html')
        value={'schema_version':3,'request_id':request_id,'source_basicops_task':'task-123','governed_parent':'parent-123','destination_profile_id':publisher.PROFILE_ID,'operation':'publish_'+kind,'credential_reference':publisher.CREDENTIAL_REFERENCE,'client_slug':client,'project_slug':kind,'prototype_kind':kind,'repository':publisher.REPOSITORY,'branch':'main','expected_base_commit':'a'*40,'source_directory':str(root),'source_package_sha256':publisher.package_digest(manifest),'source_drive_file_id':'drive-file-123','source_drive_file_sha256':index['sha256'],'source_drive_file_bytes':index['bytes'],'file_manifest':manifest,'qa_evidence_reference':'qa-123','idempotency_key':request_id,'standing_authority_reference':publisher.STANDING_AUTHORITY,'commit_message':f'prototype: {client}/{kind} approved static package'}
        value.update(updates); return value

    def test_two_clients_and_both_prototype_kinds_with_static_assets(self):
        with tempfile.TemporaryDirectory() as temporary:
            base=Path(temporary)
            for name,kind in [('alpha-source','sitemap'),('beta-source','homepage')]:
                root=base/name; root.mkdir(); publisher.validate(self.request(root,client=name.replace('-source','-health'),kind=kind))

    def test_allows_only_narrow_generated_root_and_client_readme_links(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'source'; root.mkdir(); good=self.request(root,client='alpha-health',kind='homepage')
            link=publisher.generated_index_content(good)
            for relative in ('README.md','alpha-health/README.md'):
                path=root/relative; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(link)
                good['file_manifest'].append({'path':relative,'sha256':publisher.digest_file(path),'bytes':len(link)})
            good['file_manifest'].sort(key=lambda x:x['path']); good['source_package_sha256']=publisher.package_digest(good['file_manifest'])
            publisher.validate(good)
            root_readme=root/'README.md'; root_readme.write_text('arbitrary documentation')
            item=next(x for x in good['file_manifest'] if x['path']=='README.md'); item.update(bytes=root_readme.stat().st_size,sha256=publisher.digest_file(root_readme))
            good['source_package_sha256']=publisher.package_digest(good['file_manifest'])
            with self.assertRaisesRegex(ValueError,'narrowly generated'): publisher.validate(good)

    def test_closed_schema_rejects_authority_escape_fields(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'source'; root.mkdir(); good=self.request(root)
            for key in ('command','refspec','dns','client_contact','commercial_action','production_site','workflow'):
                with self.assertRaisesRegex(ValueError,'schema'): publisher.validate({**good,key:'forbidden'})

    def test_rejects_repository_branch_traversal_dotfiles_server_code_and_sensitive_data(self):
        cases=[('../escape.html',b'x'),('.github/workflows/deploy.yml',b'x'),('config/.env',b'x'),('server.php',b'<?php'),('secret.json',b'github_pat_example')]
        for relative,data in cases:
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as temporary:
                root=Path(temporary)/'source'; root.mkdir(); files={'index.html':b'ok',relative:data}
                with self.assertRaises(ValueError): publisher.validate(self.request(root,files=files))
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'source'; root.mkdir(); good=self.request(root)
            for update in ({'repository':'other/repo'},{'branch':'cto/test'},{'client_slug':'../alpha'}):
                with self.assertRaises(ValueError): publisher.validate({**good,**update})

    def test_allows_desk_worker_audience_slugs(self):
        html=b'<a href="/audiences/desk-worker">desk-worker</a><p>desk-workers</p>'
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'source'; root.mkdir()
            self.assertEqual(publisher.validate(self.request(root,files={'index.html':html})),['alpha-health/sitemap/index.html'])

    def test_rejects_standalone_provider_tokens_and_existing_secret_patterns(self):
        provider_token=b'sk-'+b'providerToken1234567890'
        cases=[
            provider_token, b'prefix '+provider_token+b' suffix', b'token='+provider_token,
            b'{"api_key":"'+provider_token+b'"}', b'BEGIN PRIVATE'+b' KEY',
            b'github_pat_'+b'abcdefghijklmnopqrstuvwxyz', b'ghp_'+b'abcdefghijklmnopqrst',
            b'AKIA1234567890ABCDEF', b'password = value', b'client_secret: value',
        ]
        for secret in cases:
            with self.subTest(secret=secret), tempfile.TemporaryDirectory() as temporary:
                root=Path(temporary)/'source'; root.mkdir()
                with self.assertRaisesRegex(ValueError,'sensitive content detected'):
                    publisher.validate(self.request(root,files={'index.html':secret}))

    def test_rejects_symlink_and_manifest_or_package_mismatch(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'source'; root.mkdir(); good=self.request(root)
            target=root/'alpha-health/sitemap/styles/site.css'; target.unlink(); target.symlink_to(root/'alpha-health/sitemap/index.html')
            with self.assertRaisesRegex(ValueError,'manifest'): publisher.validate(good)
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'source'; root.mkdir(); good=self.request(root)
            with self.assertRaisesRegex(ValueError,'package digest'): publisher.validate({**good,'source_package_sha256':'0'*64})

    def test_rejects_drive_readback_that_does_not_match_approved_html(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'source'; root.mkdir(); good=self.request(root)
            with self.assertRaisesRegex(ValueError,'Drive readback'):
                publisher.validate({**good,'source_drive_file_sha256':'0'*64})

    def test_moved_main_fails_before_reset_or_push(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'source'; root.mkdir(); request=self.request(root)
            with mock.patch.object(publisher,'ssh_env',return_value={}), mock.patch.object(publisher,'preflight_post_publish_dependencies'), mock.patch.object(publisher,'git',side_effect=['','b'*40]) as git:
                with self.assertRaisesRegex(ValueError,'main moved'): publisher.publish(request)
                self.assertEqual(git.call_count,2)

    def test_final_push_is_guarded_by_expected_base_lease(self):
        with tempfile.TemporaryDirectory() as temporary:
            base=Path(temporary); root=base/'incoming'/'source'; root.mkdir(parents=True)
            request=self.request(root); publisher.STATE_ROOT=base/'receipts'; publisher.CHECKOUT=base/'checkout'; publisher.CHECKOUT.mkdir()
            paths=[item['path'] for item in request['file_manifest']]
            status='\0'.join(f'?? {path}' for path in paths)+'\0'
            git_results=['',request['expected_base_commit'],'','',status,'','', 'b'*40, '']
            with mock.patch.object(publisher,'ssh_env',return_value={}), \
                 mock.patch.object(publisher,'preflight_post_publish_dependencies'), \
                 mock.patch.object(publisher,'git',side_effect=git_results) as git, \
                 mock.patch.object(publisher,'run',return_value=f"{'b'*40}\trefs/heads/main"), \
                 mock.patch.object(publisher,'verify_deploy',return_value={'id':7}), \
                 mock.patch.object(publisher,'verify_public_url',return_value={'url':'https://example.test','status':200,'bytes':1,'sha256':'0'*64,'commit':'b'*40}):
                result=publisher.publish(request)
            self.assertEqual(result['commit'],'b'*40)
            push=next(call for call in git.call_args_list if call.args and call.args[0]=='push')
            self.assertIn(f"--force-with-lease=refs/heads/main:{request['expected_base_commit']}",push.args)

    def test_duplicate_idempotency_key_returns_receipt_without_git(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'source'; root.mkdir(); request=self.request(root); publisher.STATE_ROOT=Path(temporary)/'receipts'
            expected={'status':'published_and_verified','commit':'b'*40}
            publisher.store_receipt(request,expected)
            with mock.patch.object(publisher,'git') as git:
                self.assertEqual(publisher.publish(request),expected); git.assert_not_called()
            changed={**request,'qa_evidence_reference':'qa-elsewhere'}
            with self.assertRaisesRegex(ValueError,'different request'): publisher.publish(changed)

    def test_stale_interrupted_receipt_temp_does_not_block_atomic_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'source'; root.mkdir(); request=self.request(root); publisher.STATE_ROOT=Path(temporary)/'receipts'
            publisher.STATE_ROOT.mkdir(); (publisher.STATE_ROOT/f"{request['idempotency_key']}.tmp").write_text('interrupted')
            expected={'status':'published_and_verified','commit':'b'*40}
            publisher.store_receipt(request,expected)
            self.assertEqual(publisher.prior_receipt(request),expected)

    def test_publish_takes_exclusive_idempotency_lock(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'source'; root.mkdir(); request=self.request(root); publisher.STATE_ROOT=Path(temporary)/'receipts'
            with mock.patch.object(publisher.fcntl,'flock') as flock, mock.patch.object(publisher,'_publish_locked',return_value={'status':'ok'}):
                self.assertEqual(publisher.publish(request),{'status':'ok'})
                flock.assert_called_once_with(mock.ANY,publisher.fcntl.LOCK_EX)

    def test_missing_root_credential_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            publisher.SSH_KEY=Path(temporary)/'missing'; publisher.KNOWN_HOSTS=Path(temporary)/'hosts'
            with self.assertRaisesRegex(ValueError,'credential is not configured'): publisher.ssh_env()

    def test_exact_named_actions_and_bounded_http_are_success_gates(self):
        completed={'workflow_runs':[{'id':7,'name':'Deploy to lhmstaging','path':'.github/workflows/deploy.yml','head_sha':'a'*40,'status':'completed','conclusion':'success'}]}
        response=mock.MagicMock(); response.read.return_value=json.dumps(completed).encode(); response.__enter__.return_value=response
        with mock.patch.object(publisher.urllib.request,'urlopen',return_value=response):
            self.assertEqual(publisher.verify_deploy('a'*40)['id'],7)
        wrong={'workflow_runs':[{'id':8,'name':'Other','head_sha':'a'*40,'status':'completed','conclusion':'success'}]}
        response.read.return_value=json.dumps(wrong).encode()
        with mock.patch.object(publisher.urllib.request,'urlopen',return_value=response), mock.patch.object(publisher.time,'sleep'):
            with self.assertRaisesRegex(ValueError,'not observed'): publisher.verify_deploy('a'*40)

    def test_public_readback_requires_exact_index_bytes_and_hash(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'source'; root.mkdir(); request=self.request(root)
            body=(root/'alpha-health/sitemap/index.html').read_bytes()
            response=mock.MagicMock(); response.status=200; response.read.return_value=body
            response.__enter__.return_value=response
            with mock.patch.object(publisher.urllib.request,'urlopen',return_value=response):
                evidence=publisher.verify_public_url(request,'a'*40)
            self.assertEqual((evidence['bytes'],evidence['sha256']),(len(body),hashlib.sha256(body).hexdigest()))
            response.read.return_value=b'changed'
            with mock.patch.object(publisher.urllib.request,'urlopen',return_value=response):
                with self.assertRaisesRegex(ValueError,'does not match'): publisher.verify_public_url(request,'a'*40)

    def test_profile_operation_credential_authority_and_launch_negatives(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)/'source'; root.mkdir(); good=self.request(root)
            cases=[
                ({'destination_profile_id':'hosting-route-v1'},'profile'),
                ({'operation':'production_launch'},'operation'),
                ({'credential_reference':'UNIVERSAL_GITHUB_TOKEN'},'credential'),
                ({'standing_authority_reference':'UNRELATED_AUTHORITY'},'authority'),
            ]
            for update,message in cases:
                with self.subTest(update=update), self.assertRaisesRegex(ValueError,message): publisher.validate({**good,**update})

    def test_preflight_requires_repository_transport_before_mutation(self):
        with mock.patch.object(publisher.shutil,'which',side_effect=lambda name: None if name=='git' else '/bin/'+name):
            with self.assertRaisesRegex(ValueError,'repository transport'): publisher.preflight_post_publish_dependencies()

    def test_interrupted_exact_push_resumes_verification_and_one_receipt_without_commit(self):
        with tempfile.TemporaryDirectory() as temporary:
            base=Path(temporary); root=base/'incoming'/'source'; root.mkdir(parents=True)
            request=self.request(root); publisher.STATE_ROOT=base/'receipts'; publisher.CHECKOUT=base/'checkout'; publisher.CHECKOUT.mkdir()
            publisher.STATE_ROOT.mkdir(); commit='b'*40
            publisher.pending_path(request['idempotency_key']).write_text(json.dumps({'request_digest':publisher.request_digest(request),'commit':commit,'base_commit':request['expected_base_commit']}))
            with mock.patch.object(publisher,'ssh_env',return_value={}), mock.patch.object(publisher,'preflight_post_publish_dependencies'), \
                 mock.patch.object(publisher,'git',side_effect=['',commit]) as git, \
                 mock.patch.object(publisher,'verify_deploy',return_value={'id':7}), \
                 mock.patch.object(publisher,'verify_public_url',return_value={'url':'https://example.test','status':200,'bytes':1,'sha256':'0'*64,'commit':commit}):
                first=publisher.publish(request); second=publisher.publish(request)
            self.assertEqual(first,second)
            self.assertEqual(len(list(publisher.STATE_ROOT.glob('source.json'))),1)
            self.assertFalse(publisher.pending_path(request['idempotency_key']).exists())
            self.assertFalse(any(call.args and call.args[0] in {'commit','push'} for call in git.call_args_list))
            self.assertFalse(first['review_handoff']['complete'])
            self.assertTrue(first['review_handoff']['human_task_open'])
            self.assertFalse(first['review_handoff']['client_contact'])

if __name__=='__main__': unittest.main()
