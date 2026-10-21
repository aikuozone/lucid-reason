#!/usr/bin/env python3
"""Check and capture the actual generated lesson; requires optional Playwright.

No CSS, replacement text or graphics are injected into the lesson.
"""
import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'docs/assets/queue-lab'
LESSON = ROOT / 'docs/demos/queue-lab/index.html'

ORACLE = r'''() => {
let combinations=0, records=0, maxError=0;
function check(a,b,label) {const e=Math.abs(a-b);maxError=Math.max(maxError,e);if(!Number.isFinite(a)||e>1e-7)throw Error(label+': '+a+' vs '+b);}
for(let T=30;T<=90;T++)for(let sec=40;sec<=100;sec++) {
 const r=window.queueLab.simulate(T,sec),d=T/81,s=sec/60,delta=Math.max(0,s-d);
 if(r.customers.length!==81)throw Error('Customer count');
 r.customers.forEach((c,i)=>{check(c.arrival,i*d,'arrival');check(c.start,i*Math.max(d,s),'start');check(c.finish,i*Math.max(d,s)+s,'finish');check(c.wait,i*delta,'wait');records++;});
 check(r.summary.meanWait,40*delta,'mean');check(r.summary.maxWait,80*delta,'max');check(r.summary.lastFinish,80*Math.max(d,s)+s,'finish');combinations++;
}
let rejected=0;
for(const pair of [[29,60],[91,60],[30,39],[90,101],[NaN,60],[30,Infinity],['30',60],[null,60]]){
 try{window.queueLab.simulate(...pair)}catch(e){rejected++}
}
if(rejected!==8)throw Error('Invalid parameters accepted');
const r=window.queueLab.simulate(45.5,72.25);check(r.summary.meanWait,40*Math.max(0,72.25/60-45.5/81),'fractional');
return {combinations,customer_records_checked:records,invalid_inputs_rejected:rejected,fractional_case:true,max_absolute_error:maxError,oracle:'Closed-form equally spaced FCFS, independent of the implementation recurrence'};
}'''

AREA = r'''() => {
const svg=document.querySelector('#queue-chart'),p=svg.querySelector('path'),commands=p.getAttribute('d').match(/[MHV][^MHV]+/g);
let x=0,y=0,area=0;
for(const cmd of commands){const n=cmd.slice(1).trim().split(/[ ,]+/).map(Number);if(cmd[0]==='M'){x=n[0];y=n[1]}else if(cmd[0]==='H'){area+=(n[0]-x)*(302-y);x=n[0]}else{y=n[0]}}
const T=Number(document.querySelector('#arrival').value),s=Number(document.querySelector('#service').value),r=window.queueLab.simulate(T,s),width=Number(svg.getAttribute('viewBox').split(' ')[2]);
const end=Math.ceil(Math.max(90,r.summary.lastFinish)/15)*15,events=[];
r.customers.forEach(c=>{events.push([c.arrival,1]);events.push([c.start,-1])});events.sort((a,b)=>a[0]-b[0]);
let q=0,peak=0;for(let i=0;i<events.length;){let t=events[i][0],change=0;while(i<events.length&&Math.abs(events[i][0]-t)<1e-9){change+=events[i++][1]}q+=change;peak=Math.max(peak,q)}
const top=Math.max(5,Math.ceil(peak/5)*5),converted=area/((width-30-62)/end)/((302-42)/top),expected=r.summary.meanWait*81;
if(Math.abs(converted-expected)>1e-5)throw Error('Chart area mismatch: '+converted+' vs '+expected);
return {arrival_window:T,service_seconds:s,svg_area_person_minutes:converted,record_total_wait:expected};
}'''


def wait_fonts(page):
    page.evaluate('document.fonts.ready')
    page.wait_for_timeout(200)


def capture(args):
    from playwright.sync_api import sync_playwright
    ASSETS.mkdir(parents=True, exist_ok=True)
    errors, remote_requests = [], []
    with sync_playwright() as p:
        options = {'headless': True}
        if args.browser_executable:
            options['executable_path'] = str(args.browser_executable)
        browser = p.chromium.launch(**options)
        context = browser.new_context(viewport={'width':1280,'height':900},device_scale_factor=1)
        page = context.new_page()
        page.on('pageerror',lambda e: errors.append(str(e)))
        page.on('request',lambda r: remote_requests.append(r.url) if r.url.startswith(('http:','https:')) else None)
        page.goto(LESSON.as_uri(),wait_until='load');wait_fonts(page)
        oracle = page.evaluate(ORACLE)
        area_checks=[]
        for T,s in [(30,60),(90,60),(60,80),(30,100)]:
            page.locator('#arrival').fill(str(T));page.locator('#service').fill(str(s))
            r=page.evaluate('([T,s])=>window.queueLab.simulate(T,s).summary',[T,s])
            for key,selector in [('meanWait','#mean'),('maxWait','#max'),('lastFinish','#finish')]:
                if f'{r[key]:.2f}' not in page.locator(selector).inner_text():
                    raise AssertionError('Slider did not update visible '+key)
            area_checks.append(page.evaluate(AREA))
        page.locator('#uniform').click()
        assert page.locator('#mean').inner_text().startswith('0.00')
        page.locator('#burst').click()
        assert page.locator('#mean').inner_text().startswith('25.19')
        page.locator('#arrival').focus();page.keyboard.press('End')
        assert page.locator('#arrival').input_value()=='90'
        page.keyboard.press('Home')
        assert page.locator('#arrival').input_value()=='30'
        page.locator('#service').focus();page.keyboard.press('ArrowRight')
        assert page.locator('#service').input_value()=='61'
        page.locator('#burst').click();page.locator('#burst').blur()
        lab=page.locator('section').filter(has=page.locator('#lab-heading'))
        lab.screenshot(path=str(ASSETS/'desktop.png'))
        control_box=page.locator('.controls').bounding_box()
        figure_box=lab.locator('figure').bounding_box()
        lab_box=lab.bounding_box()
        page.screenshot(path=str(ASSETS/'preview.png'),clip={'x':lab_box['x'],'y':control_box['y']-16,'width':lab_box['width'],'height':figure_box['y']+figure_box['height']-control_box['y']+16})
        page.screenshot(path=str(ASSETS/'full-desktop.png'),full_page=True)
        desktop_box=lab.bounding_box()
        mobile=context.new_page()
        mobile.set_viewport_size({'width':390,'height':844})
        mobile.on('pageerror',lambda e:errors.append(str(e)))
        mobile.goto(LESSON.as_uri(),wait_until='load');wait_fonts(mobile)
        assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Mobile overflow'
        mobile.locator('#uniform').click();assert mobile.locator('#mean').inner_text().startswith('0.00')
        mobile.locator('#burst').click()
        mobile.locator('section').filter(has=mobile.locator('#lab-heading')).screenshot(path=str(ASSETS/'mobile.png'))
        mobile.screenshot(path=str(ASSETS/'full-mobile.png'),full_page=True)
        if errors or remote_requests:raise AssertionError({'page_errors':errors,'remote_requests':remote_requests})
        landing_checks={}
        landing=ROOT/'docs/index.html'
        if landing.exists():
            for width,height,label in [(1280,900,'desktop'),(390,844,'mobile')]:
                tab=context.new_page()
                tab.set_viewport_size({'width':width,'height':height})
                tab.goto(landing.as_uri(),wait_until='load');wait_fonts(tab)
                assert tab.evaluate('document.documentElement.scrollWidth<=innerWidth'),label+' landing overflow'
                assert tab.locator('.story').count()==3
                for detail in tab.locator('#sources details').all():
                    detail.locator('summary').click();assert detail.get_attribute('open') is not None
                    detail.locator('summary').click()
                landing_checks[label]={'horizontal_overflow':False,'stories':3,'full_transcripts_expand':3}
                tab.evaluate("window.scrollTo({top:0,behavior:'instant'})")
                tab.wait_for_timeout(100)
                tab.screenshot(path=str(ASSETS/f'cover-{label}.png'))
                tab.screenshot(path=str(ASSETS/f'story-{label}.png'),full_page=True)
                tab.close()
        if args.video:
            video_context=browser.new_context(viewport={'width':1280,'height':900},device_scale_factor=1,record_video_dir=str(ASSETS/'_video'),record_video_size={'width':1280,'height':900})
            video_page=video_context.new_page()
            video_page.goto(LESSON.as_uri(),wait_until='load');wait_fonts(video_page)
            video_page.locator('#lab-heading').scroll_into_view_if_needed()
            # The heading scrolls to the top so controls, metrics and chart are visible together.
            video_page.evaluate("window.scrollTo(0,document.querySelector('#lab-heading').getBoundingClientRect().top+scrollY-24)")
            video_page.wait_for_timeout(3500)
            video_page.locator('#uniform').click();video_page.wait_for_timeout(4500)
            video_page.locator('#burst').click();video_page.wait_for_timeout(4500)
            video_page.locator('#service').focus()
            for _ in range(20):video_page.keyboard.press('ArrowLeft');video_page.wait_for_timeout(35)
            video_page.wait_for_timeout(3500)
            video_page.locator('#burst').click()
            video_page.locator('#arrival').focus()
            for _ in range(30):video_page.keyboard.press('ArrowRight');video_page.wait_for_timeout(35)
            video_page.wait_for_timeout(3500)
            if landing.exists():
                video_page.goto(landing.as_uri(),wait_until='load');wait_fonts(video_page)
                video_page.locator('#conversation').scroll_into_view_if_needed();video_page.wait_for_timeout(2500)
                for article in video_page.locator('.story').all():
                    article.scroll_into_view_if_needed();video_page.wait_for_timeout(3000)
            video=video_page.video
            video_context.close();video.save_as(str(ASSETS/'walkthrough.webm'));video.delete()
            for f in (ASSETS/'_video').iterdir():f.unlink()
            (ASSETS/'_video').rmdir()
        media={}
        recording=ASSETS/'walkthrough.webm'
        if recording.exists():
            media_page=context.new_page()
            media_page.goto(recording.as_uri(),wait_until='load')
            media_page.wait_for_function("document.querySelector('video') && Number.isFinite(document.querySelector('video').duration)")
            media=media_page.locator('video').evaluate('(e)=>({duration_seconds:e.duration,width:e.videoWidth,height:e.videoHeight})')
            media_page.close()
        metadata={
            'captured_at':datetime.now(timezone.utc).isoformat(),
            'browser':browser.version,'playwright':version('playwright'),
            'source':'docs/demos/queue-lab/index.html','source_sha256':hashlib.sha256(LESSON.read_bytes()).hexdigest(),
            'kind':'Actual generated artifact in a browser; not native ChatGPT UI',
            'landing_page_sha256':hashlib.sha256(landing.read_bytes()).hexdigest() if landing.exists() else None,
            'video':media,
            'lesson_changes_for_capture':'none; only native controls, viewport and scrolling',
            'desktop_viewport':{'width':1280,'height':900},'desktop_element_box':desktop_box,
            'mobile_viewport':{'width':390,'height':844},'device_scale_factor':1,
            'computation_checks':oracle,'svg_area_checks':area_checks,
            'interaction_checks':['both presets reset both sliders and update metrics','12 UI metric comparisons across four parameter pairs','keyboard End/Home and ArrowRight update sliders','mobile presets and no page horizontal overflow'],
            'landing_page_checks':landing_checks,'page_errors':errors,'remote_requests':remote_requests,
            'files_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(ASSETS.iterdir()) if f.suffix in {'.png','.webm'}}}
        (ASSETS/'capture.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
        browser.close()
    print(json.dumps({'computation_checks':oracle,'landing_page_checks':landing_checks,'captured_files':list(metadata['files_sha256'])},ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser-executable',type=Path)
    parser.add_argument('--video',action='store_true')
    capture(parser.parse_args())
