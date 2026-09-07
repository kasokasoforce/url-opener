from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

old = '  .candidateOpen { margin-top:9px; padding:8px 11px; font-size:13px; }'
new = '  .candidateOpen, .candidateExclude { padding:8px 11px; font-size:13px; }\n  .candidateActions { display:flex; flex-wrap:wrap; gap:8px; margin-top:9px; }'
if old not in text:
    raise SystemExit('candidateOpen CSS pattern not found')
text = text.replace(old, new, 1)

old = '''    const openButton=document.createElement('button');
    openButton.type='button';
    openButton.className='candidateOpen';
    openButton.textContent='開く';
    openButton.addEventListener('click',event=>{
      event.preventDefault();
      event.stopPropagation();
      const opened=window.open(item.url,'_blank','noopener');
      status.textContent=opened?`${item.title||'作品'}を開きました`:'開けませんでした。このページのポップアップを許可してください。';
    });
    body.append(openButton);'''
new = '''    const candidateActions=document.createElement('div');
    candidateActions.className='candidateActions';
    const openButton=document.createElement('button');
    openButton.type='button';
    openButton.className='candidateOpen';
    openButton.textContent='開く';
    openButton.addEventListener('click',event=>{
      event.preventDefault();
      event.stopPropagation();
      const opened=window.open(item.url,'_blank','noopener');
      status.textContent=opened?`${item.title||'作品'}を開きました`:'開けませんでした。このページのポップアップを許可してください。';
    });
    const excludeButton=document.createElement('button');
    excludeButton.type='button';
    excludeButton.className='candidateExclude';
    excludeButton.textContent=item.duplicate?.status==='excluded'?'除外済み':'除外';
    excludeButton.disabled=item.duplicate?.status==='excluded';
    excludeButton.addEventListener('click',event=>{
      event.preventDefault();
      event.stopPropagation();
      excludeCandidate(item,checkbox,excludeButton,badge);
    });
    candidateActions.append(openButton,excludeButton);
    body.append(candidateActions);'''
if old not in text:
    raise SystemExit('candidate open block pattern not found')
text = text.replace(old, new, 1)

marker = 'async function runPreview({quiet=false}={}){'
if marker not in text:
    raise SystemExit('runPreview marker not found')
insert = '''async function excludeCandidate(item,checkbox,button,badge){
  const title=item.title||'(タイトル不明)';
  if(!confirm(`${title}\\n\\nこの作品を「除外」へ入れます。collectorには送信しません。よろしいですか？`)) return;
  const config=requireConfig();
  if(!config) return;
  const endpoint=new URL(config.endpoint);
  endpoint.pathname=endpoint.pathname.replace(/\\/manual-intake\\/?$/,'/reading-candidate-exclude');
  endpoint.search=''; endpoint.hash='';
  button.disabled=true;
  status.textContent=`${title} を除外へ送信中…`;
  try{
    const response=await fetch(endpoint.href,{
      method:'POST',
      headers:{'authorization':`Bearer ${config.token}`,'content-type':'application/json',accept:'application/json'},
      body:JSON.stringify({source:'reading-android',url:item.url,title})
    });
    let result={};
    try{result=await response.json();}catch{}
    if(!response.ok||result.ok!==true){
      const existing=result.existing?.title?` / 既存: ${result.existing.title}`:'';
      throw new Error(`${result.detail||result.error||`HTTP ${response.status}`}${existing}`);
    }
    checkbox.checked=false;
    checkbox.disabled=true;
    button.textContent='除外受付済み';
    button.disabled=true;
    badge.textContent='除外受付済み';
    updateSubmitState();
    status.textContent=`受付済み: ${title} → 除外。反映後は読むリストの重複判定にも使われます。`;
  }catch(error){
    button.disabled=false;
    status.textContent=`除外に失敗しました: ${error.message||error}`;
  }
}

'''
text = text.replace(marker, insert + marker, 1)

old = '    <div class="small">Android手動取り込みは24話以上。読むリストとの確定重複、24話未満、取得失敗、類似タイトルの要確認候補は送信できません。送信不可の作品も各カードの「開く」で個別確認できます。</div>'
new = '    <div class="small">Android手動取り込みは24話以上。読むリストとの確定重複、24話未満、取得失敗、類似タイトルの要確認候補はcollectorへ送信できません。各カードの「開く」で個別確認し、読みたくない作品はその場で「除外」へ入れられます。</div>'
if old not in text:
    raise SystemExit('help text pattern not found')
text = text.replace(old, new, 1)

path.write_text(text, encoding='utf-8')
