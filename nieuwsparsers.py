#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv 
import sys
import re
import feedparser
import os.path
import urllib.request, urllib.error, urllib.parse
import time
import csv
import os
import datetime
import urllib
from urllib import request
from time import sleep
from random import randint
from lxml import html

def polish(textstring):
#This function polishes the full text of the articles - it separated the lead from the rest by ||| and separates paragraphs and subtitles by ||.
    lines = textstring.strip().split('\n')
    lead = lines[0].strip()
    rest = '||'.join( [l.strip() for l in lines[1:] if l.strip()] )

    if rest: result = lead + ' ||| ' + rest
    else: result = lead
    return result.strip()

#Parser voor Volkskrant
def parse_vk(doc,ids,titel):
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc))
        return("","","", "")
    try:
        category=tree.xpath('//*[@class="action-bar__primary"]/div/a/text()')[0]
    except:
        category=""
    if category=="":
        try:
            category=tree.xpath('//*[@class="action-bar__primary"]/a/text()')[0] 
        except:
            category="" 
            print("oops - geen category")
    try:
        textfirstpara=tree.xpath('//*/header/p/text()')[0].replace("\n", "").strip()  
    except:
        textfirstpara=""
    if textfirstpara=="":
        try:
            textfirstpara=tree.xpath('//*/header/p/text()')[1].replace("\n", "").strip()
        except:
            textfirstpara=" "
            print("oops - geen first para")
    try:
        #1. path: regular textrest 
        #2. path: textrest version found in 2014 11 16
        #3. path: second heading found in 2014 11 50
        #4. path: text with link behind; found in 2014 10 2455(html-file-nr)
        #5. path: old design regular text
        #6. path: old design second heading
        #7. path:old design text with link        
        textrest=tree.xpath('//*/div[@class="article__body"]/*/p[*]/text() | //*[@class="article__body__container"]/p[*]/text() | //*[@class="article__body__container"]/h3/text() | //*[@class="article__body__container"]/p/a/text() | //*[@id="art_box2"]/p/text() | //*[@id="art_box2"]/p/strong/text() | //*[@id="art_box2"]/p/a/text() | //*/p[@class="article__body__paragraph first"]/text() | //*/div[@class="article__body"]/h2/text()')
        #print("Text rest: ")
        #print(textrest)
    except:
        print("oops - geen text?")
        textrest=""
    text = textfirstpara + "\n"+ "\n".join(textrest)
    try:
        author_door=" ".join(tree.xpath('//*/span[@class="author"]/*/text() | //*/span[@class="article__body__container"]/p/sub/strong/text()')).strip().lstrip("Bewerkt").lstrip(" door:").lstrip("Door:").strip()
        # geeft het eerste veld: "Bewerkt \ door: Redactie"  
        if author_door=="edactie":
            author_door = "redactie"
    except:
        author_door=""
    if author_door=="":
        try:
            author_door=tree.xpath('//*[@class="author"]/text()')[0].strip().lstrip("Bewerkt").lstrip(" door:").lstrip("Door:").strip()
            if author_door=="edactie":
                author_door = "redactie"
        except:
            author_door=""
            print("oops - geen auhtor?")
    try:
        author_bron=" ".join(tree.xpath('//*/span[@class="article__meta"][*]/text()')).strip().lstrip("Bron:").strip()
        # geeft het tweede veld: "Bron: ANP"                          
    except:
        author_bron=""
    if author_bron=="":
        try:
            author_bron=" ".join(tree.xpath('//*/span[@class="author-info__source"]/text()')).strip().lstrip("- ").lstrip("Bron: ").strip()
        except:
            author_bron=""
    if author_bron=="":
        try:
            bron_text=tree.xpath('//*[@class="time_post"]/text()')[1].replace("\n", "")
            author_bron=re.findall(".*?bron:(.*)", bron_text)[0]
        except:
            author_bron=""
        if author_bron=="":
            try:
                bron_text=tree.xpath('//*[@class="time_post"]/text()')[0].replace("\n", "")
                author_bron=re.findall(".*?bron:(.*)", bron_text)[0]
            except:
                author_bron=""
                print("oops - geen bron")
    if author_door=="" and author_bron=="" and category=="Opinie":
        author_door = "OPINION PIECE OTHER AUTHOR"
    text=polish(text)
    print("Category: ")
    print(category)
    print("Title: ")
    print(titel)
    print("Text: ")
    print(text)
    print("Auhtor: ")
    print(author_door)
    print("Bron: ")
    print(author_bron)

    return(titel,text.strip(),category.strip(),author_door.replace("\n", " ").strip(),author_bron.replace("\n"," ").strip())



#Parser voor Nu 
def parse_nu(doc,ids,titel):
    tree = html.fromstring(doc)
    try:
        category = tree.xpath('//*[@class="block breadcrumb "]/div/div/ul/li[2]/a/text()')[0]
        if category == "":
            print("OOps - geen category?")
    except:
        category=""
        print("OOps - geen category?")
    try:
        textfirstpara=tree.xpath('//*[@data-type="article.header"]/div/div[1]/div[2]/text()')[0]
    except:
        print("OOps - geen eerste alinea?")
        textfirstpara=""
    try:
        #1.path: regular paragraphs 
        #2.path: paragraphs with xpath"span" included 
        #3.path: italic text found in: nunieuw jan 2015 96
        #4.path: second order heading found in: nunieuw jan 2015 227
        #5.path: link+italic (displayed underlined) text found in: nunieuw jan 2015 1053
        #6.path: second version for link+italic (displayed underlined) text found in: nunieuw jan 2015 4100
        #7.path: link (displayed underlined, not italic) text found in: nunieuw dec 2014 5
        #8.path: bold text found in: nunieuw nov 2014 12
        textrest=tree.xpath('//*[@data-type="article.body"]/div/div/p/text() | //*[@data-type="article.body"]/div/div/p/span/text()| //*[@data-type="article.body"]/div/div/p/em/text() | //*[@data-type="article.body"]/div/div/h2/text() | //*[@data-type="article.body"]/div/div/h3/text() | //*[@data-type="article.body"]/div/div/p/a/em/text() | //*[@data-type="article.body"]/div/div/p/em/a/text() | //*[@data-type="article.body"]/div/div/p/a/text() | //*[@data-type="article.body"]/div/div/p/strong/text()')   
        if textrest == "":
            print("OOps - empty textrest for?")
    except:
        print("OOps - geen text?")
        textrest=""
    text = textfirstpara + "\n"+ "\n".join(textrest)
    try:
        #regular author-xpath:
        author_door = tree.xpath('//*[@class="author"]/text()')[0].strip().lstrip("Door:").strip()
        if author_door == "":
            # xpath if link to another hp is embedded in author-info            
            try: 
                author_door = tree.xpath('//*[@class="author"]/a/text()')[0].strip().lstrip("Door:").strip()
            except:
                author_door=""
                print("OOps - geen author for?")
    except:
        author_door="" 
        print("OOps - geen author?")
    author_bron = ""
    text=polish(text)
    print("Title: ")
    print(titel)
    print("Category: ")
    print(category)
    print("Text: ")
    print(text)
    print("Auhtor: ")
    print(author_door)
    print("Bron: ")
    print(author_bron)

    return(titel,text.strip(),category.strip(),author_door.replace("\n", " ").strip(),author_bron.replace("\n"," ").strip())


#Parser for Nrc
def parse_nrc(doc,ids,titel):
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc))
        print(doc)
        return("","","", "")
    try:
        category = tree.xpath('//*[@id="broodtekst"]/a[1]/text()')[0]
    except:
        category = ""
    if category=="":
        try:
            category=tree.xpath('//*[@class="article__section-branding"]/text()')[0]
        except:
            category=""
    try:
        #1. path: type 1 layout: regular text
        #2. path: type 1 layout: text with link behind
        #3. path: type 1 layout: text bold
        #4. path: type 1 layout: text bold and italic
        #5. path: type 2 layout: normal text first paragraph
        #6. path: type 2 layout: text with link behind
        #7. path: type 1 layout: italic text, found in 2014 11 988
        #8. path for in beeld found 2015 11 13
        textfirstpara=tree.xpath('//*[@class="eerste"]/text() | //*[@class="eerste"]/a/text() | //*[@class="eerste"]/strong/text() | //*[@class="eerste"]/strong/em/text() | //*[@id="article-content"]/p[1]/text() | //*[@id="article-content"]/p[1]/a/text() | //*[@class="eerste"]/em/text() | //*[@class="intro"]/text() | //*[@class="intro"]/p/text() | //*[@class="intro"]/p/span/text()')
        textfirstpara = " ".join(textfirstpara)
    except:
        textfirstpara=""
        print("Ooops geen first para")
    try:
        #1. path: type 1 layout: regular text
        #2. path: type 1 layout: second heading in regular text
        #3. path: type 2 layout: text in different layout, found in 2014 12 11
        #4. path: type 2 layout: bold text, found in 2014 12 11
        #5. path: type 2 layout: text with underlying link, found in 2014 12 11
        #6. path: type 2 layout: italic text, found in 2014 12 11
        #7. path: type 2 layout: second heading found in 2014 12 11
        #8. path: type 2 layout: text in grey box/ speech bubble
        #9. path: type 1 layout: text with link behind
        #10.path: type 1 layout: text in grey box/ speech bubble
        #11. path: type 1 layout: bold text found in 2014 12 198
        #12. path: type 1 layout: italix text with link behind, found in 2014 12 198 !!!!!not working :(
        #13. path: type 3 layout: regular text found in 2014 11 62
        #14. path: type 3 layout: text with link behind found in 2014 11 63
        #15. path: type 3 layout: italic text with link behind, found in 2014 11 63
        #16. path: type 1 layout: italix text, found in 2014 04 500
        #17. path: type 1 layout: found 2015 11 13
        #17. path: type 1 layout: heading in regular text found 2015 11 13
        #18. live feed subheading "old news"
        #19. live feed text "old news"
        #20. live feed textlink "oldnews"
        #21. live feed list "old news"
        #21. live feed subheading "new news"
        #22. live feed text "new news"
        #23. live feed textlink "new news"
       #24. live feed names "new news"
        #24. path type 1 layout: subheading in regular text found 2015 11 16
        #25. path type 1 layout: text in link found on 2015 11 16
        #26. path regular layout: bold subtitle found 2015 11 16
        textrest=tree.xpath('//*[@id="broodtekst"]/p[position()>1]/text() | //*[@id="broodtekst"]/h2/text() | //*[@id="article-content"]/p[position()>1]/text() | //*[@id="article-content"]/p[position()>1]/strong/text() | //*[@id="article-content"]/p[position()>1]/a/text() | //*[@id="article-content"]/p[position()>1]/em/text() | //*[@id="article-content"]/h2/text() | //*[@id="article-content"]/blockquote/p/text() | //*[@id="broodtekst"]/p[position()>1]/a/text() | //*[@id="broodtekst"]/blockquote/p/text() | //*[@id="broodtekst"]/p[position()>1]/strong/text() | //*[@id="broodtekst"]/p[position()>1]/a/em/text() | //*[@class="beschrijving"]/text() | //*[@class="beschrijving"]/a/text() | //*[@class="beschrijving"]/a/em/text() | //*[@id="broodtekst"]/p[position()>1]/em/text() | //*[@class="content article__content"]/p[position()>0]/text() | //*[@class="content article__content"]/p/strong/text() | //*[@class="content article__content"]/p/a/text() | //*[@class="content article__content"]/blockquote/p/text() | //*[@class="bericht"]/h2/text() | //*[@class="bericht"]/p/text() | //*[@class="bericht"]/p/a/text() |//*[@class="bericht"]/ul/li/text() | //*[@class="bericht bericht--new"]/h2/text() | //*[@class="bericht bericht--new"]/p/text() | //*[@class="bericht bericht--new"]/p/a/text() | //*[@class="bericht bericht--new"]/p/em/text() | //*[@class="content article__content"]/h2/text() | //*[@class="content article__content"]/h3/text() | //*[@class="content article__content"]/p/a/em/text() | //*[@class="content article__content"]/blockquote/p/strong/text() | //*[@class="content article__content"]/p/br/a/strong/text() | //*[@class="content article__content"]/p/em/text()')
    except:
        print("oops - geen text?")
        textrest = ""
    text = textfirstpara + "\n"+ "\n".join(textrest)
    textnew=re.sub("Follow @nrc_opinie","",text)
    try:
        author_door = tree.xpath('//*[@class="author"]/span/a/text()')[0]
    except:
        author_door = ""
    if author_door == "":
        try:
            author_door = tree.xpath('//*[@class="auteur"]/span/a/text()')[0]
        except:
            author_door = ""
    if author_door == "":
        try:
            author_door = tree.xpath('//*[@class="authors"]/ul/li/text()')[0]
        except:
            author_door = ""
    if author_door=="":
        try: 
            author_door=tree.xpath('//*[@class="article__byline__author-and-date"]/a/text()')[0]
        except:
            author_door = ""
    author_bron=""
    if textnew=="" and category=="" and author_door=="":
        print("No article-page?")
        try:
            if tree.xpath('//*[@class="kies show clearfix"]/h2/text()')[0] == 'Lees dit hele artikel':
                text="THIS SEEMS TO BE AN ARTICLE ONLY FOR SUBSCRIBERS"
                print(" This seems to be a subscribers-only article")   
        except:
            text=""
    text=polish(text)
    print("Title: ")
    print(titel)
    print("Category: ")
    print(category)
    print("Text: ")
    print(textnew)
    print("Auhtor: ")
    print(author_door)

    return(titel,text.strip(),category.strip(),author_door.replace("\n", " ").strip(),author_bron.replace("\n"," ").strip())
    

def parse_telegraaf(doc,ids,titel):
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc))
        return("","","","")
    try:
        category = tree.xpath('//*[@class="selekt"]/text()')[0]
    except:
        category = ""
        print("OOps - geen category?")
    try:
        #1.path: layout 1: regular first para
        #2.path: layout 2 (video): regular first (and mostly only) para
        #3.path: layout 1: second version of first para, fi 2014 11 6
        #4.path layout 1: place found on 2015 11 16
        textfirstpara=tree.xpath('//*[@class="zak_normal"]/p/text() \
        | //*[@class="bodyText streamone"]/div/p/text() \
        | //*[@class="zak_normal"]/text() | //*[@class="zak_normal"]/span/text()')
        textfirstpara = " ".join(textfirstpara)
    except:
        textfirstpara=""
        print("OOps - geen textfirstpara?")
    try:
        #1. path: layout 1: regular text, fi 2014 12 006
        #2. path: layout 1: text with link, fi 2014 12 006
        #3. path: layout 1: second heading, fi 2014 12 015
        #4. path: layout 1: bold text, fi 2014 12 25
        #5. path: layout 1: italic text, fi 2014 09 5200
        #6. path: layout 1: second headings, fi 2014 07 84
        textrest=tree.xpath('//*[@id="artikelKolom"]/p[not (@class="tiptelegraaflabel")]/text() | //*[@id="artikelKolom"]/p/a/text() | //*[@id="artikelKolom"]/h2/strong/text() | //*[@id="artikelKolom"]/p/strong/text() | //*[@id="artikelKolom"]/p/em/text() | //*[@id="artikelKolom"]/h2[not (@class="destination trlist")]/text() | //*[@class="broodtekst"]/p/text() | //*[@class="broodtext"]/h2/strong/text()')
    except:
        print("oops - geen texttest?")
        textrest = ""
    text = textfirstpara + "\n"+ "\n".join(textrest)
    try:
        author_door = tree.xpath('//*[@class="auteur"]/text()')[0].strip().lstrip("Van ").lstrip("onze").lstrip("door").strip()
    except:
        author_door = ""
    author_bron=""
    text=polish(text)
    print("Title: ")
    print(titel)
    print("Category: ")
    print(category)
    print("Text: ",type(text))
    print(text)
    print("Auhtor: ")
    print(author_door)
    print("Bron: ")
    print(author_bron)

    return(titel,text.strip(),category.strip(),author_door.replace("\n", " ").strip(),author_bron.replace("\n"," ").strip())


def parse_spits(doc,ids,titel):
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc))
        return("","","","")
    try:
        category = tree.xpath('//*[@class="active"]/text()')[0]
    except:
        category = ""
        print("OOps - geen category?")
    #fix: xpath for category in new layout leads to a sentence in old layout:
    if len(category.split(" ")) >1:
        category=""            
    try:
        #1. path: regular text
        #2. path: text with link behind, fi 2014 12 646
        #3. path: italic text, fi 2014 12 259
        #4. path: second headings, fi 2014 12 222
        #5. path: another version of regualr formated text, fi 2014 12 1558
        #6. path: another version a second heading, fi 2014 12 1923
        #7. path: italic text with link behind in span environment, fi 2014 11 540
        #8. path: italic text with link behind, not in span evir, fi 2014 10 430
        #old layout:
        #9. path: regular text
        #10. path: text with link behind, fi 2014 08 12
        #11. path: italic text, fi 2014 08 19
        #12. path: second heading, fi 2014 08 411
        #13. path: another version of regular text, fi 2014 08 840
        #14. path: second heading fitting 13.path regular text, fi 2014 08 840
        #15. path: italic text, fitting 13. path, fi 2014 08 840
        #seems like again another layout/html-structure
        #16. path: regular text, fi 2014 07 749
        #17. path: also regular text, fi 2014 07 749
        #18. path: (probabaly second layout): underlined, text with link, fi 2014 07 1251
        #19. path: and another version of regular text fi 2014 06 626
        #20. path: text with link behind, fi 2014 06 626
        #21. path: another version of italic text fi 2014 06 626
        #22. path: another version of italic text with link behind, fi 2014 06 1024
        #23. path: yet another regular text, fi 2014 06 1471
        #24. path: again, regular text, fi 2014 06 1547
        #25. path: text with link, matches text in path 24, fi 2014 06 1547
        #26. path: bold text, matches text in path 24, fi 2014 06 1547
        #27. path: another regula rtext, fi 2014 05 437
        #28. path: italic text, fits path 27., fi 2014 05 437
        #30. path: again regular text, fi 2014 04 50
        #31. path: text with link behind, fi 2014 04 50
        #32. path: another regular text, fi 2014 03 667
        #33. path: 2nd heading, matches 32. patch, fi 2014 03 667
        #33. path: text with link, matches 32. patch, fi 2014 03 667
        textrest=tree.xpath('//*[@class="field field-name-body field-type-text-with-summary field-label-hidden"]/div/div/p/text() | //*[@class="field field-name-body field-type-text-with-summary field-label-hidden"]/div/div/p/a/text() | //*[@class="field field-name-body field-type-text-with-summary field-label-hidden"]/div/div/p/em/text() | //*[@class="field field-name-body field-type-text-with-summary field-label-hidden"]/div/div/h2/text() | //*[@class="field field-name-body field-type-text-with-summary field-label-hidden"]/div/div/p/span/text() | //*[@class="field field-name-body field-type-text-with-summary field-label-hidden"]/div/div/h2/span/text() | //*[@class="article"]/div/p/text() | //*[@class="field field-name-body field-type-text-with-summary field-label-hidden"]/div/div/p/span/em/a/text() | //*[@class="field field-name-body field-type-text-with-summary field-label-hidden"]/div/div/p/em/a/text() | //*[@class="article"]/p/a/text() | //*[@class="article"]/p/em/text() | //*[@class="article"]/p/strong/text() | //*[@class="article"]/div/text() | //*[@class="article"]/div/strong/text() | //*[@class="article"]/div/em/text() | //*[@class="article"]/div/div/p/text() | //*[@class="article"]/div/p/text() | //*[@class="article"]/p/em/a/text() | //*[@class="article"]/p/span/text() | //*[@class="article"]/p/span/a/text() | //*[@class="article"]/p/span/em/text() | //*[@class="article"]/p/a/em/text() | //*[@class="article"]/div/div/div/p/text() | //*[@class="article"]/div/div/text() | //*[@class="article"]/div/div/a/text() | //*[@class="article"]/div/div/strong/text() |//*[@id="artikelKolom"]/div/div/p/text() | //*[@id="artikelKolom"]/div/div/p/em/text() | //*[@class="article"]/p/font/text() | //*[@class="article"]/p/font/a/text() | //*[@class="article"]/div/div/div/text() | //*[@class="article"]/div/div/div/strong/text() | //*[@class="article"]/div/div/div/a/text() |  //*[@class="field field-name-body field-type-text-with-summary field-label-hidden"]/div/div/p/strong/text() |  //*[@class="field field-name-body field-type-text-with-summary field-label-hidden"]/div/div/ul/li/text()')
    except:
        print("oops - geen texttest?")
        textrest = ""
    text = "\n".join(textrest)
    try:
        #new layout author:
        author_door = tree.xpath('//*[@class="username"]/text()')[0].strip().lstrip("door ").strip()
    except:
        author_door = ""
    if author_door=="": 
        #try old layout author
        try:
            author_door = tree.xpath('//*[@class="article-options"]/text()')[0].split("|")[0].replace("\n", "").replace("\t","").strip()
        except:
            author_door = ""        
    author_bron=""
    text=polish(text)
    print("Title: ")
    print(titel)
    print("Category: ")
    print(category)
    print("Text: ")
    print(text)
    print("Auhtor: ")
    print(author_door)
    print("Bron: ")
    print(author_bron)

    return(titel,text.strip(),category.strip(),author_door.replace("\n", " ").strip(),author_bron.replace("\n"," ").strip())


def parse_metronieuws(doc,ids,titel):
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc))
        return("","","","")
    try:
        category = tree.xpath('//*[@class="active"]/text()')[0]
    except:
        category = ""
    #fix: xpath for category in new layout leads to a sentence in old layout:
    if len(category.split(" ")) >1:
        category=""            
    try:
        #1. path: regular text
        #2. path: text with link behind, fi 2014 12 646
        #3. path: italic text, fi 2014 12 259
        #4. path: second headings, fi 2014 12 222
        #5. path: another version of regualr formated text, fi 2014 12 1558
        #6. path: another version a second heading, fi 2014 12 1923
        #7. path: italic text with link behind in span environment, fi 2014 11 540
        #8. path: italic text with link behind, not in span evir, fi 2014 10 430
        #--until here code is just copied from spits
        #10. path: bold and italic text, fi 2014 12 04
        #11. path: bold text, fi 2014 12 04
        #12. path: second headings
        #13. path: regular text
        textrest=tree.xpath('//*[@class="field-item even"]/p/text() | //*[@class="field-item even"]/p/a/text() | //*[@class="field-item even"]/p/em/text() | //*[@class="field-item even"]/h2/text() | //*[@class="field-item even"]/p/span/text() | //*[@class="field-item even"]/h2/span/text() | //*[@class="field-item even"]/p/span/em/a/text() | //*[@class="field-item even"]/p/em/a/text() | //*[@class="field-item even"]/p/em/strong/text() | //*[@class="field-item even"]/p/b/text() | //*[@class="field-item even"]/div/text() | //*[@class="field-item even"]/p/strong/text()') 
    except:
        print("oops - geen textrest?")
        textrest = ""
    text = "\n".join(textrest)
    textnew=re.sub("Lees ook:"," ",text)
    try:
        #new layout author:
        author_door = tree.xpath('//*[@class="username"]/text()')[0].strip().lstrip("door ").lstrip("© ").lstrip("2014 ").strip()
    except:
        author_door = ""
    if author_door=="": 
        #try old layout author
        try:
            author_door = tree.xpath('//*[@class="article-options"]/text()')[0].split("|")[0].replace("\n", "").replace("\t","").strip()
        except:
            author_door = ""        
    author_bron=""
    textnew=polish(textnew)
    print("Titel: ")
    print(titel)
    print("Category: ")
    print(category)
    print("Text: ")
    print(textnew)
    print("Auhtor: ")
    print(author_door)
    print("Bron: ")
    print(author_bron)

    return(titel,textnew.strip(),category.strip(),author_door.replace("\n", " ").strip(),author_bron.replace("\n"," ").strip())

#Parser for Trouw
def parse_trouw(doc,ids,titel):
    try:
        tree=html.fromstring(doc)
    except:
        print("kon dit niet parsen", type(doc), len(doc))
    try:
        category=tree.xpath('//*[@id="subnav_nieuws"]/li/a/span/text()')[0]
    except:
        category="" 
    if category=="":
        try:
            category=tree.xpath('//*[@id="str_cntr2"]//*[@class="dos_default dos_film"]/h2/text()')[0]
        except:
            category=""
    if category=="":
        try:
            category=tree.xpath('//*[@id="str_cntr2"]//*[@class="dos_default dos_vluchtelingen"]/span/text()')[0]
        except:
            category=""
            print("oops - geen category")

    #try:
    #    textfirstpara=tree.xpath('//*[@class="art_box2"]//*[@class="intro"]/text()')
    #except:
    #    textfirstpara=" "
    #    print("oops - geen text")

    try:
        #1. Regular text - intro
        #2. Bold text - subtitles
        #3. Regular  text
        #4. Extra box title
        #5. Extra box text
        #6. Link text
        #7. Explanantion box text
        #8. italics
        textrest=tree.xpath('//*[@class="art_box2"]//*[@class="intro"]/text() | //*[@id="art_box2"]/p/strong/text() | //*[@id="art_box2"]/p/text() | //*[@id="art_box2"]/section/h3/text() | //*[@id="art_box2"]/section/p/text() |  //*[@id="art_box2"]/p/a/text() |  //*[@id="art_box2"]//*[@class="embedded-context embedded-context--inzet"]/text() |  //*[@id="art_box2"]/p/em/text()')
    except:
        textrest=" "
        print("oops - geen textrest")
    text = "\n".join(textrest)

    #text=textfirstpara + "\n" + "\n".join(textrest)
    
    try:
        author_door=tree.xpath('//*[@class="author"]/text()')[0] 
        #if author_door=="bewerkt door redactie":
            #author_door="redactie"
    except:
        author_door=" "
        print("geen author")

    try:
        bron_text=tree.xpath('//*[@class="time_post"]/text()')[1].replace("\n", "")
        author_bron=re.findall(".*?bron:(.*)", bron_text)[0]
    except:
        author_bron=""
    if author_bron=="":
        try: 
            bron_text=tree.xpath('//*[@class="time_post"]/text()')[0].replace("\n", "")
            author_bron=re.findall(".*?bron:(.*)", bron_text)[0]
        except: 
            author_bron=""
            print("geen bron")

    textnew=polish(text)
   
    print("Titel: ")
    print(titel)
    print("Category: ")
    print(category)
    print("Text: ")
    print(textnew)
    print("Auhtor: ")
    print(author_door)
    print("Bron: ")
    print(author_bron)
 
    return(titel,textnew.strip(),category.strip(),author_door.replace("\n", " ").strip(),author_bron.replace("\n"," ").strip())

#Parser for Parool
def parse_parool(doc,ids,titel):
    try:
        tree=html.fromstring(doc)
    except:
        print("kon dit niet parsen", type(doc),len(doc))
    try:
        category=tree.xpath('//*[@id="hdr_col4"]//*[@class="active"]/b[2]/text()')[0]
    except:
        category="" 
        print("oops - geen category")
    try:
        textfirstpara=tree.xpath('//*[@id="art_box2"]//*[@class="intro2"]/text() | //*[@id="art_box2"]//*[@class="intro2"]/a/text()')
        textfirstparanew=" ".join(textfirstpara)
    except:
        textfirstpara=" "
        print("oops - geen textfirstpara")
    try:
        #1. Regular text
        #2. Bold text - subtitles
        #3. Link text
        #4. Embedded text subtitle one
        #5. Embedded text subitles rest
        textrest=tree.xpath('//*[@id="art_box2"]/p/text() | //*[@id="art_box2"]/p/strong/text() | //*[@id="art_box2"]/p/a/text() | //*[@id="embedding"]/div/div/div/strong/text() |//*[@id="embedding"]/div/div/div/font/strong/text() |  //*[@id="embedding"]/div/div/div/font/text() |  //*[@id="embedding"]/div/div/div/font/a/text()')
    except:
        textrest=" "
        print("oops - geen textrest")
    text=textfirstparanew + "\n" + "\n".join(textrest)
    author_text=tree.xpath('//*[@id="art_box2"]/text()')
    try:
        author_door=[e for e in author_text if e.find("Door")>=0][0].strip().replace("(","").replace(")","").replace("Door:","")
    except:
        author_door=""
    if author_door=="":
        try:
            author_door=[e for e in author_text if e.find("Bewerkt door:")>=0][0].strip().replace("(","").replace(")","").replace("Bewerkt door:","")
        except:
            author_door=""
            print("ooops - geen author_door")
    try:
        bron_text=tree.xpath('//*[@id="art_box2"]//*[@class="time_post gen_left"]/text()')[0]
        author_bron=re.findall(".*?Bron:(.*)", bron_text)[0]
    except:
        author_bron=" "
        print("geen bron")
    
    textnew=polish(text)

    print("Titel: ")
    print(titel)
    print("Category: ")
    print(category)
    print("Text: ")
    print(textnew)
    print("Auhtor: ")
    print(author_door)
    print("Bron: ")
    print(author_bron)
    
    return(titel,textnew.strip(),category.strip(),author_door.replace("\n", " ").strip(),author_bron.replace("\n"," ").strip())

#Parser voor NOS
def parse_nos(doc,ids,titel):
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc))
        return("","","", "")
    try:
        category="".join(tree.xpath('//*[@id="content"]/article/header/div/div/div/div/span/a/text()'))
    except:
        category=""
    if category=="":
        try:
            category="".join(tree.xpath('//*[@id="content"]/article/header/div/div/div/div/div/div/span/a/text()'))
        except:
            category=""
            print("ooops - geen category")
    try:
        textfirstpara=tree.xpath('//*/header/p/text()')[0].replace("\n", "").strip()  
    except:
        textfirstpara=""
    if textfirstpara=="":
        try:
            textfirstpara=tree.xpath('//*[@id="content"]/article/section/div/div/p/text()')[0]
        except:
            textfirstpara=" "
            print("oops - geen first para")
    try:
        #1. Regular text.
        #2. Italics text.
        #3. Link.
        #4. Subtitle
        #5. Table subtitle
        textrest=tree.xpath('//*[@id="content"]/article/section/div/div/p/text() | //*[@id="content"]/article/section/div/div/p/i/text() | //*[@id="content"]/article/section/div/div/p/a/text() | //*[@id="content"]/article/section/div/div/h2/text() | //*[@id="content"]/article/section/div/h2/text() | //*[@id="content"]/article/section/div/div/table/tbody/tr/td/text()')
        #print("Text rest: ")
        #print(textrest)
    except:
        print("oops - geen text?")
        textrest=""
    text ="\n".join(textrest)
    try:
        author_door=tree.xpath('//*[@id="content"]/article/section/div/div/div/span/text()')[0]
    except:
        author_door=""
        print("ooops - geen author")
    author_bron=""
    text=polish(text)
    print("Category: ")
    print(category)
    print("Title: ")
    print(titel)
    print("Text: ")
    print(text)
    print("Auhtor: ")
    print(author_door)

    return(titel,text.strip(),category.strip(),author_door.replace("\n", " ").strip(),author_bron)


#Parser voor Tpo
def parse_tpo(doc,ids,titel):
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc))
        return("","","", "")
    try:
        category="".join(tree.xpath('//*[@class="articleTop"]//*[@class="catLabel"]/text()')).strip()
    except:
        category=""
    if category=="":
        try:
            category="".join(tree.xpath('//*[@id="content"]/article/header/div/div/div/div/div/div/span/a/text()'))
        except:
            category=""
            print("ooops - geen category")
    try:
        #1. Regular text.
        #2. Link.
        #3. Italics text
        #4. Subtitle
        #5. Text in cat. Video
        #6. Italics link
        textrest=tree.xpath('//*[@itemprop="articleBody"]/p/text() | //* [@itemprop="articleBody"]/p/a/text() | //*[@itemprop="articleBody"]/p/em/text() | //*[@itemprop="articleBody"]/h2/text() | //*[@itemprop="articleBody"]/text() | //*[@itemprop="articleBody"]/p/a/em/text() | //*[@itemprop="articleBody"]/h4/text() | //*[@itemprop="articleBody"]/p/b/text()')
        #print("Text rest: ")
        #print(textrest)
    except:
        print("oops - geen text?")
        textrest=""
    text ="\n".join(textrest)
    try:
        author_door=tree.xpath('//*[@class="authorDescriptionBody"]/h3/a/span/text()')[0]
    except:
        author_door=""
    if author_door=="":
        try:
            author_door=tree.xpath('//*[@class="articleTop"]/div/span/a/text()')[0]
        except:
            author_door=""
            print("ooops - geen author_door")
    author_bron=""

    text=polish(text)
    print("Category: ")
    print(category)
    print("Title: ")
    print(titel)
    print("Text: ")
    print(text)
    print("Auhtor: ")
    print(author_door)

    return(titel,text.strip(),category.strip(),author_door.replace("\n", " ").strip(),author_bron)


#Parser for Geenstijl
def parse_geenstijl(doc,ids,titel):
    try:
        tree=html.fromstring(doc)
    except:
        print("kon dit niet parsen", type(doc),len(doc))
    try:
        #1. Regular text with picture
        #2. Link text  with picture
        #3. Italics text wth picture
        #4. Bold text with picture
        #5. Crossed text with picture
        #6. Regular text alternative (no picture)
        #7. Link text alternative (no picture)
        #8. Crossed text alternative (no picture)
        #9. Italics text alternative (no picture)
        #10. Bold text alternative (no picture)
        #11. Bold text link alternative (no picture)
        #12. Italics link text alternative (no picture)
        #11. Tweet quoted in the article
        #12. Tweet quoted in the article - author
        #13. Tweet quoted in the article - date 
        textrest=tree.xpath('//*[@id="content"]/article/text() | //*[@id="content"]/article/a/text() | //*[@id="content"]/article/em/text() | //*[@id="content"]/article/strong/text() | //*[@id="content"]/article/s/text() |  //*[@id="content"]/article/p/text() | //*[@id="content"]/article/p/a/text() | //*[@id="content"]/article/p/s/text() | //*[@id="content"]/article/p/em/text() | //*[@id="content"]/article/p/strong/text() | //*[@id="content"]/article/p/strong/a/text() | //*[@id="content"]/article/p/em/a/text() | //*[@id="content"]/article/blockquote/p/text() | //*[@id="content"]/article/blockquote/text() | //*[@id="content"]/article/blockquote/a/text()')
    except:
        textrest=" "
        print("oooops - geen textrest")
    text="\n".join(textrest)
    try:
        author_door=tree.xpath('//*[@id="content"]/article/footer/text()')[0].replace("|","")
    except:
        author_door=""
        print("ooops - geen author_door")
    category=""
    author_bron=""
    text=polish(text)

    print("Title: ")
    print(titel)
    print("Text: ")
    print(text)
    print("Auhtor: ")
    print(author_door)

    return(titel,text.strip(),category,author_door.strip(),author_bron)


#Parser voor sargasso
def parse_sargasso(doc,ids,titel):
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc))
        return("","","", "")
    try:
        category=tree.xpath('//*[@id="content"]/article//*[@class="thema-meta"]/a/text()')[0]
    except:
        category=""
        print("ooops - geen category")
    if category=="":
        category="SG-café"
    try:
        #1. Regular text.
        #2. Link text
        #3. Italics
        #4. Italics link
        #5. Italics link
        #6. Bold text
        #7. Italics subtitle
        #8. Blockquote
        #9. Blockquote bold
        #10 Colored text
        #11. List
        #12. Blockquote bold
        textrest=tree.xpath('//*[@id="content"]/article/div/p/text() | //*[@id="content"]/article/div/p/a/text() | //*[@id="content"]/article/div/p/em/text() | //*[@id="content"]/article/div/p/em/a/text() | //*[@id="content"]/article/div/p/a/em/text() | //*[@id="content"]/article/div/p/strong/text() | //*[@id="content"]/article/div/p/i/text() | //*[@id="content"]/article/div/blockquote/p/text() | //*[@id="content"]/article/div/blockquote/p/em/text() | //*[@id="content"]/article/div//em/span/text() | //*[@id="content"]/article/div/ul/li/text() | //*[@id="content"]/article/div/blockquote/p/strong/text()')
        #print("Text rest: ")
        #print(textrest)
    except:
        print("oops - geen text?")
        textrest=""
    text ="\n".join(textrest)
    try:
        author_door=tree.xpath('//*[@id="content"]/article//*[@class="by-author"]/a/text()')[0]
    except:
        author_door=""
        print("ooops - geen author")
    author_bron=""
    text=polish(text)
    print("Category: ")
    print(category)
    print("Title: ")
    print(titel)
    print("Text: ")
    print(text)
    print("Auhtor: ")
    print(author_door)

    return(titel,text.strip(),category.strip(),author_door.replace("\n", " ").strip(),author_bron)

#Parser vook Fok
def parse_fok(doc,ids,titel):
    try:
        tree = html.fromstring(doc)
    except:
        print("kon dit niet parsen",type(doc),len(doc))
        return("","","","")
    try:
        category = "".join(tree.xpath('//*[@id="crumbs"]/ul/li/a/text()'))
    except:
        category = ""
    #fix: xpath for category in new layout leads to a sentence in old layout:
    if len(category.split(" ")) >1:
        category=""            
    try:
        #1. path: regular text
        #2. path: bold text
        #3. path: bold text link
        #4. path: link
        textrest=tree.xpath('//*[@role="main"]/article/p/text() | //*[@role="main"]/article/p/strong/text() | //*[@role="main"]/article/p/strong/a/text() | //*[@role="main"]/article/p/a/text() | //*[@role="main"]/article/p/em/text()') 
    except:
        print("oops - geen textrest?")
        textrest = ""
    text = "\n".join(textrest)
    textnew=re.sub("Lees ook:"," ",text)
    try:
        #new layout author:
        author_door = tree.xpath('//*[@class="mainFont"]/text()')[0].strip()
    except:
        author_door = ""
    if author_door=="": 
        #try old layout author
        try:
            author_door = tree.xpath('//*[@class="article-options"]/text()')[0].split("|")[0].replace("\n", "").replace("\t","").strip()
        except:
            author_door = ""        
    try:
        author_bron=tree.xpath('//*[@class="bron"]/strong/text()')[0]
    except:
        author_bron=""
    if author_bron=="":
        try:
            author_bron=tree.xpath('//*[@class="bron"]/strong/a/text()')[0]
        except:
            author_bron=""
            print("geen bron")
    textnew=polish(textnew)
    print("Titel: ")
    print(titel)
    print("Category: ")
    print(category)
    print("Text: ")
    print(textnew)
    print("Auhtor: ")
    print(author_door)
    print("Bron: ")
    print(author_bron)

    return(titel,textnew.strip(),category.strip(),author_door.replace("\n", " ").strip(),author_bron.strip())

 
if __name__ == "__main__":
     print("\n")
     print("Welkom bij rsshond 0.2 (by Damian Trilling, www.damiantrilling.net)")
     print("Current date & time: " + time.strftime("%c"))
     print("\n")
     print("Please do not run this file seperately, it only contains the parsers themselves")
