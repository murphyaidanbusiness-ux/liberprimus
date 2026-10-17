import re
FW=set("""THE A AN OF TO IN AND OR NOR BUT FOR WITH BY ON AT FROM AS IS ARE WAS WERE BE BEEN BEING AM IT ITS THIS THAT THESE THOSE HE SHE HIS HER HERS HIM THEY THEM THEIR THEIRS WE US OUR OURS YOU YOUR YOURS I ME MY MINE NOT NO WHICH WHO WHOM WHOSE WHAT WHEN WHERE WHY HOW IF THAN THEN SO HAVE HAS HAD HAVING DO DOES DID DONE WILL WOULD CAN COULD SHALL SHOULD MAY MIGHT MUST ALL ANY SOME EACH THERE HERE UPON INTO OVER UNDER ABOUT ALSO ONLY VERY SUCH WITHOUT WITHIN THROUGH BETWEEN AFTER BEFORE ABOVE BELOW UNTO THOU THEE THY THINE THYSELF YE HATH DOTH DOETH ART SHALT WILT""".split())
THEOFTO=frozenset(['THE','OF','TO'])
def rm(*ws): return frozenset(ws)
ARCH_EXC=set('IS WAS HAS THIS HIS AS US YES NOTHING THUS ITS WHOSE'.split())
def archaic(stream):
    out=[];prev=''
    for i,t in enumerate(stream):
        if t in '.;': out.append(t); prev=''; continue
        w=t
        if t=='YOU':
            w='THEE' if prev in ('TO','FOR','WITH','UNTO','OF','FROM','BY','UPON','IN','ON','AT') else 'THOU'
        elif t=='YOUR': w='THY'
        elif t=='YOURS': w='THINE'
        elif t=='YOURSELF': w='THYSELF'
        elif t=='ARE' and prev in ('THOU',): w='ART'
        elif prev in ('HE','SHE','IT','WHO','GOD','LORD','MAN') and t.endswith('S') and len(t)>=4 and t not in ARCH_EXC:
            if t=='DOES': w='DOETH'
            elif t.endswith('ES') : w=t[:-2]+'ETH'
            else: w=t[:-1]+'ETH'
        elif prev in ('HE','SHE','IT','WHO','GOD') and t=='HAS': w='HATH'
        out.append(w); prev=t if t!='YOU' else w
    return out
# (label, remove-set, mode, archaic?)
VARIANTS=[
 ('base (Cicada rules)',frozenset(),'cic',False),
 ('base, ING kept',frozenset(),'cic_ing',False),
 ('-THE',rm('THE'),'cic',False),
 ('-THE/OF',rm('THE','OF'),'cic',False),
 ('-THE/OF/TO',THEOFTO,'cic',False),
 ('-THE/OF/TO/AND',rm('THE','OF','TO','AND'),'cic',False),
 ('-THE/OF/TO/A',rm('THE','OF','TO','A'),'cic',False),
 ('-THE/A/AN',rm('THE','A','AN'),'cic',False),
 ('-THE/OF/TO/AND/A/IN',rm('THE','OF','TO','AND','A','IN'),'cic',False),
 ('-all function words',frozenset(FW),'cic',False),
 ('letters (no digraphs)',frozenset(),'letters',False),
 ('letters -THE/OF/TO',THEOFTO,'letters',False),
 ('TH-only merged',frozenset(),'th',False),
 ('TH-only -THE/OF/TO',THEOFTO,'th',False),
 ('archaic (thou/thee/-eth)',frozenset(),'cic',True),
 ('archaic -THE/OF/TO',THEOFTO,'cic',True),
]
