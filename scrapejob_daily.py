#!/usr/bin/env python3

from inca import Inca
import time
myinca = Inca()

accounts = ['abertis', 'grupoacsnews', 'amadeusitgroup', 'popular', 'grupobpopular', 'popularenlinea', 'bancosabadell', 'sabadellprensa', 'bankia', 'bankinter', 'bbva', 'bbva_esp', 'accionistascabk', 'infocaixa', 'enagas', 'endesa', 'endesaclientes', 'quejasendesa', 'ferrovial', 'ferrovial_es', 'siemensgamesa', 'gnf_es', 'gnfclientes_es', 'gnfprensa_es', 'grifols_press', 'iberdrola', 'tuiberdrola', 'inditexspain', 'mapfre', 'mapfre_atiende', 'mapfre_es', 'redelectricaree', 'repsol', 'bancosantander', 'santander', 'telefonica', 'abnamro', 'abnamro_news', 'aegon', 'aegon_nl', 'AalbertsIndustr', 'AkzoNobel', 'altice', 'arcelormittal', 'arcelormittalnl', 'asmlcompany', 'boskalisnl', 'dsm', 'dsmnederland', 'GalapagosNV', 'gemalto', 'heineken', 'heineken_nl', 'heinekencorp', 'heinekennl_corp', 'ing', 'ing_groep', 'nn_group', 'nn_nederland', 'philips', 'randstad', 'randstadnl', 'RELXGroupHQ', 'SBMSchiedam', 'shell', 'shell_nederland', 'vopak_nederland', 'wolters_kluwer', 'aholddelhaize', 'aholdnews', 'unilever', 'unilevernl', 'AstraZeneca', 'AstraZenecaUK', 'santander', 'santanderuk', 'barclays', 'barclaysuk', 'barclaysukhelp', 'barclaysuknews', 'BHPBilliton', 'bp_plc', 'bp_uk', 'BATPress', 'bt_uk', 'btcare', 'btgroup', 'compassgroupuk', 'Diageo_GB', 'Diageo_news', 'GSK', 'Glencore', 'hsbc', 'hsbc_uk', 'imperialbrands', 'imptobuk', 'asklloydsbank', 'lbgnews', 'lloydsbanknews', 'grid_media', 'nationalgriduk', 'Prudential', 'pruadviser', 'pruukpress', 'rbs', 'rbs_help', 'discoverrb', 'riotinto', 'shell', 'shellstationsuk', 'shireplc', 'stanchart', 'Unilever', 'unileveruki', 'Vodafone', 'VodafoneUK']


for account in accounts:
    time.sleep(60)    # rate limits should be handled automatically, but this does not seem to always work. quick and dirty fix is sleeping here
	myinca.clients.twitter_timeline(screen_name=account)

