"""Node/browser-boundary tests. Fake pages do not prove live Chromium rendering."""
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).with_name('visual_qa.mjs').resolve().as_uri()


def node(code):
    result = subprocess.run(['node', '--input-type=module', '-e',
        f'import * as qa from {json.dumps(MODULE)};\n' + code], capture_output=True, text=True, timeout=15)
    if result.returncode:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


class VisualTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.run = self.root / 'ted-route-12-dm34-revision1'
        self.source = self.run / 'source'
        self.output = self.run / 'output'
        self.output.mkdir(mode=0o700, parents=True)
        self.pages = ['luminary-counselling/homepage/' + name for name in
            ('index.html', 'about-tara.html', 'how-i-can-help.html', 'online-counselling.html', 'fees-and-getting-started.html')]
        self.entries = []
        for page in self.pages:
            target = self.source / page
            target.parent.mkdir(parents=True, exist_ok=True)
            data = b'<html><meta name="robots" content="noindex"><h1>Prototype</h1></html>'
            target.write_bytes(data)
            self.entries.append({'path': page, 'sha256': hashlib.sha256(data).hexdigest(), 'size_bytes': len(data)})
        self.entries.sort(key=lambda item: item['path'])
        self.manifest = {'schema_version': 1, 'files': self.entries, 'pages': self.pages,
            'package_sha256': hashlib.sha256(json.dumps(self.entries, sort_keys=True, separators=(',', ':')).encode()).hexdigest()}
        self.save()

    def save(self):
        (self.run / 'source-manifest.json').write_text(json.dumps(self.manifest))

    def args(self):
        return json.dumps(str(self.source)), json.dumps(str(self.output)), json.dumps(str(self.root))

    def test_run_path_scope_and_traversal(self):
        source, output, root = self.args()
        result = node(f'''const p=qa.runPaths({source},{output},{root});
let rejected=false;try{{qa.runPaths('/tmp/unregistered/source','/tmp/elsewhere/output',{root});}}catch{{rejected=true;}}
console.log(JSON.stringify({{source:p.source,rejected}}));''')
        self.assertEqual(result['source'], str(self.source))
        self.assertTrue(result['rejected'])

    def test_exact_manifest_reads_and_hashes_all_five_pages(self):
        source, output, root = self.args()
        result = node(f'''const p=qa.runPaths({source},{output},{root});const m=await qa.loadManifest(p,{{requireRoot:false}});
console.log(JSON.stringify({{count:m.files.size,hash:m.manifest.package_sha256}}));''')
        self.assertEqual(result['count'], 5)
        self.assertEqual(result['hash'], self.manifest['package_sha256'])

    def assert_manifest_rejected(self):
        source, output, root = self.args()
        self.assertTrue(node(f'''let rejected=false;try{{await qa.loadManifest(qa.runPaths({source},{output},{root}),{{requireRoot:false}});}}catch{{rejected=true;}}
console.log(JSON.stringify(rejected));'''))

    def test_changed_source_rejected(self):
        (self.source / self.pages[0]).write_bytes(b'changed')
        self.assert_manifest_rejected()

    def test_unlisted_file_rejected(self):
        (self.source / 'injected.js').write_text('console.log(1)')
        self.assert_manifest_rejected()

    def test_symlink_file_rejected(self):
        target = self.source / self.pages[0]
        target.unlink(); target.symlink_to(self.source / self.pages[1])
        self.assert_manifest_rejected()

    def test_wrong_page_scope_rejected(self):
        self.manifest['pages'] = self.pages[:-1]
        self.save()
        self.assert_manifest_rejected()

    def test_static_server_only_serves_manifest_get_head(self):
        source, output, root = self.args()
        result = node(f'''const m=await qa.loadManifest(qa.runPaths({source},{output},{root}),{{requireRoot:false}});
const s=await qa.staticServer(m.files);const a=await fetch(s.origin+'/prototypes/'+qa.PAGES[0]);
const b=await fetch(s.origin+'/prototypes/'+qa.PAGES[0],{{method:'POST',body:'never submit'}});
const c=await fetch(s.origin+'/outside.html');await new Promise(r=>s.server.close(r));
console.log(JSON.stringify([a.status,b.status,c.status,qa.packagePath('/%2e%2e/secret')]));''')
        self.assertEqual(result, [200, 405, 404, None])

    def test_dom_failure_detection(self):
        result = node('''const errors=qa.checkDom({h1:[],noindex:false,scrollWidth:500,viewportWidth:390,
missingImages:['missing.png'],reducedMotion:false,motion:['sun']});console.log(JSON.stringify(errors));''')
        self.assertEqual(len(result), 6)

    def test_cross_page_fragments_checked_without_navigation(self):
        result = node('''const results=[{page:'one',ids:['a'],links:[{href:'two#missing',target:'two',fragment:'missing'}],errors:[],status:'passed'},
{page:'two',ids:['b'],links:[],errors:[],status:'passed'}];qa.fragments(results);console.log(JSON.stringify(results[0]));''')
        self.assertEqual(result['status'], 'failed')
        self.assertIn('missing fragment', result['errors'][0])

    def test_full_fake_browser_boundary_ten_screenshots_network_and_mobile_menu(self):
        source, output, root = self.args()
        result = node(f'''
import fs from 'node:fs/promises';
const seen={{routes:[],contexts:[],clicks:0,escapes:0,closed:0}};
const dom={{h1:['Prototype'],noindex:true,scrollWidth:390,viewportWidth:390,missingImages:[],reducedMotion:true,motion:[],ids:['primary-nav'],links:[]}};
const browser={{async newContext(options){{seen.contexts.push(options);return {{
async route(pattern,fn){{await fn({{request:()=>({{url:()=> 'https://booking.example.com/submit'}}),abort:reason=>seen.routes.push(reason),continue:()=>seen.routes.push('continued')}});}},
async routeWebSocket(pattern,fn){{fn({{close:()=>seen.routes.push('websocket-closed')}});}},
async newPage(){{let open=false;return {{on(){{}},async goto(){{return {{status:()=>200}};}},async evaluate(){{return dom;}},
locator(selector){{if(selector==='[data-booking-choice]') return {{count:async()=>0}};return selector.startsWith('button')?{{count:async()=>1,isVisible:async()=>true,click:async()=>{{open=true;seen.clicks++;}},getAttribute:async()=>String(open)}}:{{isVisible:async()=>open}};}},
keyboard:{{press:async key=>{{if(key==='Escape'){{open=false;seen.escapes++;}}}}}},
screenshot:async options=>fs.writeFile(options.path,Buffer.from('fake PNG bytes')),close:async()=>{{seen.closed++;}} }};}},
async close(){{}} }};}},async close(){{}} }};
const receipt=await qa.run({source},{output},{{root:{root},requireRoot:false,playwright:{{chromium:{{launch:async options=>{{seen.launch=options;return browser;}}}}}}}});
console.log(JSON.stringify({{status:receipt.status,semantic:receipt.semantic_qa_approved,count:receipt.pages.length,seen,
hashes:receipt.pages.every(page=>/^[a-f0-9]{{64}}$/.test(page.screenshot.sha256)),manifest:receipt.source_package_sha256}}));''')
        self.assertEqual(result['status'], 'mechanical_passed')
        self.assertFalse(result['semantic'])
        self.assertEqual(result['count'], 10)
        self.assertEqual(result['seen']['clicks'], 5)
        self.assertEqual(result['seen']['escapes'], 5)
        self.assertEqual(result['seen']['closed'], 10)
        self.assertEqual(result['seen']['routes'], ['blockedbyclient', 'websocket-closed'] * 2)
        self.assertEqual([item['viewport']['width'] for item in result['seen']['contexts']], [1440, 390])
        self.assertTrue(result['hashes'])
        self.assertTrue((self.output / 'mechanical-qa.json').exists())
        self.assertEqual(result['manifest'], self.manifest['package_sha256'])



BOOKING_FAKE = r"""
function bookingPage(options={}) {
  const initial='http://127.0.0.1:1234/prototypes/luminary-counselling/homepage/fees-and-getting-started.html';
  const original='Choose either option above.';
  const state={url:initial,message:original,focused:false,clicks:[],reloads:0};
  const handlers=new Map();
  const panel={count:async()=>options.missingPanel?0:1,isVisible:async()=>true,
    getAttribute:async name=>name==='aria-live'?(options.badLive?'off':'polite'):'-1'};
  const message={count:async()=>options.missingMessage?0:1,isVisible:async()=>true,textContent:async()=>state.message};
  return {state,url:()=>state.url,on:(event,fn)=>handlers.set(event,fn),off:event=>handlers.delete(event),
    locator(selector){
      if(selector==='[data-booking-choice]')return {count:async()=>options.absent?0:2};
      if(selector==='#booking-placeholder')return panel;
      if(selector==='#booking-placeholder [data-choice-message]')return message;
      const choice=selector.includes('"session"')?'session':'conversation';
      return {count:async()=>1,isVisible:async()=>true,getAttribute:async()=>options.unsafeHref?'https://booking.example/submit':'#booking-placeholder',
        click:async()=>{
          state.clicks.push(choice);
          if(!(options.brokenBranch&&choice==='conversation'))state.message=options.sameMessage?'Same choice':choice==='session'?'You chose a full session.':'You chose an introductory conversation.';
          state.focused=!options.noFocus;
          state.url=options.navigate?'http://127.0.0.1:1234/other':initial+(options.noHash?'':'#booking-placeholder');
          if(options.backend&&handlers.has('request'))handlers.get('request')({method:()=> 'POST',url:()=> 'https://booking.example/submit?private=hidden'});
        }};
    },
    waitForFunction:async(fn,before)=>{if(!state.focused||state.message===before)throw new Error('timed out');},
    evaluate:async()=>state.focused,
    goto:async url=>{state.reloads++;state.url=url;state.message=original;state.focused=false;return {status:()=>200};}
  };
}
"""


class BookingChoiceTests(unittest.TestCase):
    def result(self, options=None):
        return node(BOOKING_FAKE + 'const page=bookingPage(' + json.dumps(options or {}) + ');'
                    + 'const result=await qa.bookingChoices(page);console.log(JSON.stringify({result,state:page.state}));')

    def test_both_distinct_branches_have_focus_and_fragment_on_both_viewports(self):
        for viewport in (1440, 390):
            with self.subTest(viewport=viewport):
                outcome = self.result({'viewport': viewport})
                result = outcome['result']
                self.assertEqual(result['status'], 'passed')
                self.assertEqual([branch['choice'] for branch in result['branches']], ['session', 'conversation'])
                self.assertNotEqual(result['branches'][0]['message'], result['branches'][1]['message'])
                self.assertTrue(all(branch['focused'] and branch['fragmentMatched'] and branch['stayedOnPage'] for branch in result['branches']))
                self.assertEqual(outcome['state']['clicks'], ['session', 'conversation'])
                self.assertEqual(outcome['state']['message'], 'Choose either option above.')
                self.assertNotIn('#', outcome['state']['url'])
                self.assertEqual(outcome['state']['reloads'], 1)

    def test_old_prototype_without_widget_is_skipped(self):
        outcome = self.result({'absent': True})
        self.assertEqual(outcome['result']['status'], 'not_present')
        self.assertFalse(outcome['result']['present'])
        self.assertEqual(outcome['state']['clicks'], [])
        self.assertEqual(outcome['state']['reloads'], 0)

    def test_inert_conversation_branch_fails(self):
        outcome = self.result({'brokenBranch': True})
        self.assertEqual(outcome['result']['status'], 'failed')
        self.assertEqual(outcome['result']['branches'][0]['status'], 'passed')
        self.assertEqual(outcome['result']['branches'][1]['status'], 'failed')
        self.assertEqual(outcome['state']['reloads'], 1)

    def test_identical_messages_fail(self):
        result = self.result({'sameMessage': True})['result']
        self.assertEqual(result['status'], 'failed')
        self.assertTrue(any('not distinct' in error for error in result['errors']))

    def test_missing_panel_or_message_blocks_clicks(self):
        for options in ({'missingPanel': True}, {'missingMessage': True}, {'badLive': True}):
            with self.subTest(options=options):
                outcome = self.result(options)
                self.assertEqual(outcome['result']['status'], 'failed')
                self.assertEqual(outcome['state']['clicks'], [])

    def test_focus_or_fragment_failure_is_reported(self):
        for options in ({'noFocus': True}, {'noHash': True}, {'navigate': True}):
            with self.subTest(options=options):
                result = self.result(options)['result']
                self.assertEqual(result['status'], 'failed')
                self.assertEqual(len(result['branches']), 2)

    def test_unsafe_backend_anchor_never_clicked(self):
        outcome = self.result({'unsafeHref': True})
        self.assertEqual(outcome['result']['status'], 'failed')
        self.assertEqual(outcome['state']['clicks'], [])

    def test_backend_attempt_fails_and_receipt_omits_query(self):
        result = self.result({'backend': True})['result']
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['backendRequests'], ['POST https://booking.example/submit'] * 2)
        self.assertNotIn('private=hidden', json.dumps(result))


if __name__ == '__main__':
    unittest.main()
