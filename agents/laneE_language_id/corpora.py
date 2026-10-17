import re, os, html, json, glob, unicodedata, pickle
S='.'
HERE=S+'/agents/laneE_language_id'
CORP=HERE+'/corp'
DK=S+'/dl/dukotah/liber-primus'
K18=DK+'/data/keys/armada18/'; K19=DK+'/data/keys/armada19/'
SPECIAL={'þ':'TH','Þ':'TH','ð':'TH','Ð':'TH','æ':'AE','Æ':'AE','œ':'OE','Œ':'OE','ƿ':'W','Ƿ':'W','ß':'SS','ø':'O','Ø':'O','ł':'L','Ł':'L','đ':'D','Đ':'D','ı':'I','İ':'I','ƕ':'HW','ʒ':'G','ȝ':'G','ſ':'S','ĸ':'K','ħ':'H'}
WORDRE=re.compile(r"[^\W\d_]+(?:['’ʼ][^\W\d_]+)*|[.!?]+|[;:]")
def norm_word(w):
    w=w.replace("'",'').replace('’','').replace('ʼ','')
    out=[]
    for ch in w:
        if ch in SPECIAL: out.append(SPECIAL[ch]); continue
        d=unicodedata.normalize('NFKD',ch)
        out.append(''.join(c for c in d if not unicodedata.combining(c)))
    w=''.join(out).upper()
    w=re.sub('[^A-Z]','',w)
    return w
def tokenize(text):
    """-> stream of tokens: words (A-Z) , '.' strong end, ';' weak end"""
    st=[]
    for m in WORDRE.finditer(text):
        t=m.group(0)
        if t[0] in '.!?': st.append('.')
        elif t in ';:': st.append(';')
        else:
            w=norm_word(t)
            if w: st.append(w)
    return st
def strip_gutenberg(t):
    m=re.search(r'\*\*\* ?START OF[^\n]*\n',t)
    if m: t=t[m.end():]
    m=re.search(r'\*\*\* ?END OF',t)
    if m: t=t[:m.start()]
    return t
def read(path,start=0,end=None):
    return open(path,encoding='utf-8',errors='ignore').read()[start:end]
def from_text(path,gut=True,start=0,end=None):
    t=read(path,start,end)
    if gut: t=strip_gutenberg(t)
    return tokenize(t)
def from_conllu(path,limit=None):
    st=[]
    for l in open(path,encoding='utf-8',errors='ignore'):
        if l.startswith('# text ='):
            st+=tokenize(l[8:].strip()); st.append('.')
    return st
def from_bible_xml(path):
    t=open(path,encoding='utf-8',errors='ignore').read()
    segs=re.findall(r'<seg[^>]*>(.*?)</seg>',t,flags=re.S)
    txt=' '.join(html.unescape(re.sub('<[^>]+>',' ',s)).strip() for s in segs)
    return tokenize(txt)
def from_html_dir(paths):
    st=[]
    for p in paths:
        t=open(p,encoding='utf-8',errors='ignore').read()
        t=re.sub(r'<br[^>]*>','\n',t); t=re.sub('<[^>]+>',' ',t); t=html.unescape(t)
        m=re.search(r'Next\s',t); 
        if m: t=t[m.end():]
        st+=tokenize(t)
    return st
def sentences(stream,level='strong'):
    """list of sentences (list of words). level strong: '.' ends; medium: '.' and ';' end"""
    out=[];cur=[]
    for t in stream:
        if t=='.' or (t==';' and level=='medium'):
            if cur: out.append(cur); cur=[]
        elif t==';': pass
        else: cur.append(t)
    if cur: out.append(cur)
    return out
def build_all():
    C={}   # name -> (stream, lang, register)
    def add(name,stream,lang,reg):
        n=sum(1 for t in stream if t not in '.;')
        if n>=3000: C[name]=(stream,lang,reg)
        else: print('skip small',name,n)
    # ---- English prose / registers
    en=[('Moby Dick',K18+'melville_moby_dick.txt','novel'),('Plato Republic (Jowett)',K18+'plato_republic_jowett.txt','philosophy'),
        ('Emerson Essays I',K18+'emerson_essays_first_series.txt','emerson'),('Emerson Essays II',K18+'emerson_essays_second_series.txt','emerson'),
        ('Emerson Self-Reliance',DK+'/data/keys/self_reliance.txt','emerson'),
        ('Agrippa Occult Phil I',K18+'agrippa_occult_philosophy_book1_1651jf.txt','occult'),('Agrippa Occult Phil II',K18+'agrippa_occult_philosophy_book2_1651jf.txt','occult'),
        ('Agrippa Occult Phil III',K18+'agrippa_occult_philosophy_book3_1651jf.txt','occult'),
        ('Blavatsky Secret Doctrine I',K18+'blavatsky_secret_doctrine_v1.txt','occult'),('Crowley Book of Lies',K18+'crowley_book_of_lies_clean.txt','occult'),
        ('Crowley Book of the Law',K18+'crowley_book_of_the_law_hermetic.txt','occult'),('Crowley Liber 777',K18+'crowley_liber777_clean.txt','occult'),
        ('Manly Hall Initiates Flame',K18+'manly_hall_initiates_flame.txt','occult'),('Levi History of Magic',K18+'levi_history_of_magic.txt','occult'),
        ('Lovecraft Mountains Madness',K18+'lovecraft_mountains_madness.txt','fiction'),('Lovecraft Dunwich',K18+'lovecraft_dunwich_horror.txt','fiction'),
        ('Poe Complete Works',K18+'poe_complete_works.txt','fiction'),('Mabinogion (Guest, English)',K18+'mabinogion_vol1_guest_edwards_ed.txt','myth'),
        ('Homer Odyssey (Butler)',K18+'homer_odyssey_butler.txt','myth'),('Dante Inferno (Longfellow)',K18+'dante_inferno_longfellow.txt','verse-tr'),
        ('KJB Genesis',K18+'kjb_genesis.txt','kjv'),('KJB Psalms',K18+'kjb_psalms.txt','kjv'),('KJB Ecclesiastes',K18+'kjb_ecclesiastes.txt','kjv'),
        ('KJB Revelation',K18+'kjb_revelation.txt','kjv'),('KJB John',K18+'kjb_gospel_john.txt','kjv'),
        ('KJB Isaiah',K19+'kjb_isaiah.txt','kjv'),('KJB Job',K19+'kjb_job.txt','kjv'),('KJB Ezekiel',K19+'kjb_ezekiel.txt','kjv'),
        ('KJV Bible (whole)',DK+'/analysis/bookcipher/books/kjv.txt','kjv'),('Tyndale NT',K19+'tyndale_new_testament.txt','kjv'),
        ('Douay-Rheims',K19+'bible_douay_rheims.txt','kjv'),
        ('Tao Te Ching (Legge)',K19+'tao_te_ching_legge.txt','eastern'),('Bhagavad Gita (Arnold)',K19+'bhagavad_gita_arnold.txt','eastern'),
        ('Upanishads (Hume)',K19+'upanishads_hume.txt','eastern'),('Gospel of Buddha (Carus)',K19+'gospel_of_buddha_carus.txt','eastern'),
        ('Nietzsche Twilight Idols',K19+'nietzsche_twilight_idols.txt','philosophy'),('Kant CPR',K19+'kant_critique_pure_reason.txt','philosophy'),
        ('Schopenhauer World as Will',K19+'schopenhauer_world_will.txt','philosophy'),('Leibniz Theodicy',K19+'leibniz_theodicy.txt','philosophy'),
        ('Bacon Novum Organum',K19+'bacon_novum_organum.txt','philosophy'),('Aristotle Nic. Ethics',K19+'aristotle_nicomachean_ethics.txt','philosophy'),
        ('Mill On Liberty',K19+'mill_on_liberty.txt','philosophy'),('Paine Age of Reason',K19+'paine_age_of_reason.txt','philosophy'),
        ('Plato Symposium',K19+'plato_symposium.txt','philosophy'),('Plato Timaeus',K19+'plato_timaeus.txt','philosophy'),
        ('Cicero Tusculan (English tr.)',K19+'cicero_tusculan_disputations.txt','philosophy'),('Suetonius (English tr.)',K19+'suetonius_twelve_caesars.txt','history'),
        ('Lucretius (English tr.)',K19+'lucretius_nature_things.txt','philosophy'),('Gibbon Decline Fall I',K19+'gibbon_decline_fall_v1.txt','history'),
        ('Bunyan Pilgrim Progress',K19+'bunyan_pilgrims_progress.txt','archaic'),('Shelley Frankenstein',K19+'shelley_frankenstein.txt','fiction'),
        ('Stoker Dracula',K19+'stoker_dracula.txt','fiction'),('Voltaire Candide (tr.)',K19+'voltaire_candide.txt','fiction'),
        ('De Quincey Opium Eater',K19+'dequincey_opium_eater.txt','essay'),('Declaration of Independence',K18+'declaration_of_independence.txt','legal'),
        ('Magna Carta',K18+'magna_carta.txt','legal'),
        ('Cicada 2012-13 puzzle texts',K18+'cicada_2012_2013_puzzle_texts.txt','cicada'),('Cicada koans + LP sections',K18+'cicada_koans_and_lp_sections.txt','cicada'),
        ('Cicada LP1 solved (English)',K18+'lp1_english_forward.txt','cicada'),
        ('SCRATCH Tao (english_tao)',S+'/corp/english_tao.txt','eastern'),
        ]
    for name,p,reg in en:
        if os.path.exists(p): add(name,from_text(p,gut=True),'en',reg)
        else: print('missing',p)
    # nltk gutenberg
    ng=CORP+'/nltk/gutenberg/'
    for f,name,reg in [('whitman-leaves.txt','Whitman Leaves of Grass','verse'),('blake-poems.txt','Blake Poems','verse'),('milton-paradise.txt','Milton Paradise Lost','verse'),
                       ('shakespeare-hamlet.txt','Shakespeare Hamlet','verse'),('shakespeare-macbeth.txt','Shakespeare Macbeth','verse'),
                       ('austen-emma.txt','Austen Emma','novel'),('carroll-alice.txt','Carroll Alice','novel'),('chesterton-ball.txt','Chesterton Ball','novel')]:
        add(name,tokenize(read(ng+f,0,None)),'en',reg)
    # ---- other languages
    add('Latin: Newton Principia',from_text(DK+'/analysis/latin/latin_28233.txt',gut=False,start=20000,end=700000),'la','prose')
    add('Latin: Caesar BG',from_text(S+'/corp/caesar.txt',gut=False),'la','prose')
    add('Latin: Virgil Aeneid',from_text(K19+'virgil_aeneid_latin.txt'),'la','verse')
    add('Latin: Vulgate Genesis',from_text(S+'/corp/vulgate_gen.txt',gut=False),'la','bible')
    add('Latin: Cicero (SCRATCH)',from_text(S+'/corp/cicero.txt',gut=False),'la','prose')
    add('Latin: Vulgate (bible-corpus)',from_bible_xml(CORP+'/bible_la.xml'),'la','bible')
    add('Latin: PROIEL treebank',from_conllu(CORP+'/la.conllu'),'la','prose')
    add('Old English: Beowulf',tokenize('\n'.join(l for l in read(DK+'/analysis/round10b/B6-non-english-plaintext/corpora/oe_beowulf.txt').split('\n') if re.search('[þðæÞÐÆ]',l))),'ang','verse')
    ps=sorted(glob.glob(CORP+'/oe_sacred/html/*/*.html')+glob.glob(CORP+'/oe_sacred/html/*/*/*.htm'))
    add('Old English: Sacred-Texts corpus (poetry+psalms)',from_html_dir(ps),'ang','verse')
    add('German: Faust',from_text(DK+'/analysis/round10b/B6-non-english-plaintext/corpora/de_faust.txt',gut=False,start=5000),'de','verse')
    add('German: bible-corpus',from_bible_xml(CORP+'/bible_de.xml'),'de','bible')
    for code,nm in [('eo','Esperanto'),('fi','Finnish'),('hu','Hungarian'),('tr','Turkish'),('nl','Dutch'),('fr','French'),('it','Italian'),('es','Spanish'),('no','Norwegian'),('sv','Swedish'),('da','Danish'),('mi','Maori')]:
        add(nm+': bible-corpus',from_bible_xml(CORP+'/bible_%s.xml'%code),code,'bible')
    add('English: bible-corpus (modern)',from_bible_xml(CORP+'/bible_en.xml'),'en','kjv')
    add('Gothic: Wulfila Bible (PROIEL)',from_conllu(CORP+'/got.conllu'),'got','bible')
    add('Welsh: CCG treebank',from_conllu(CORP+'/cy.conllu'),'cy','prose')
    add('Icelandic: IcePaHC (hist.)',from_conllu(CORP+'/is.conllu'),'is','prose')
    add('Faroese: FarPaHC',from_conllu(CORP+'/fo.conllu'),'fo','prose')
    add('Irish: IDT',from_conllu(CORP+'/ga.conllu'),'ga','prose')
    add('Basque: BDT',from_conllu(CORP+'/eu.conllu'),'eu','prose')
    add('Estonian: EDT',from_conllu(CORP+'/et.conllu'),'et','prose')
    add('English: EWT (web)',from_conllu(CORP+'/en_ewt.conllu'),'en','web')
    # Old Norse sagas
    fs=sorted(glob.glob(CORP+'/on_perseus/plain_text/*/*.txt'))
    st=[]
    for f in fs: st+=tokenize(read(f))
    add('Old Norse: sagas (Perseus/CLTK)',st,'non','prose')
    return C
if __name__=='__main__':
    C=build_all()
    pickle.dump(C,open(HERE+'/streams.pkl','wb'))
    for k,(st,l,r) in C.items():
        w=[t for t in st if t not in '.;']; print('%-48s %-4s %-9s words=%8d sents=%6d'%(k,l,r,len(w),sum(1 for t in st if t=='.')))
