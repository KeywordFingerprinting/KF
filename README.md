# KeywordFingerprinting

# Prerequisite:
	1.Create directories for pcaps, csvs (after parsing pcaps), features, and libsvm 
	input files
	
	mkdir ~/Trace
	mkdir ~/Trace/part2 
	mkdir ~/Trace/part2/libsvm  //directory libsvm input files
	mkdir ~/Trace/part2/feature //directory for features (e.g.,Total.csv, cumulTLS.csv)
	mkdir ~/Trace/part2/csv     //directory for csvs after parsing pcaps using tshark
	mkdir ~/Trace/part2/pcap    //directory for pcaps

        ** All csv files are not uploaded in data folder and can be provided upon request.

# Directory description:
	1.Classifiers: svm, knn, and kFP
		We used Wang et al.'s knn[1] proposed in Usenix14 and Hayes and Danezis's kFP[2] 
		in Usenix16.
	2.Data: dataset we used in experiments
	- monitored: monitored keyword traces for Google_incremental, Google_oneshot, Bing, 
	  Duckduckgo, and Google_blacklisted, AOL search queries
	- back: background traces for Google, Duckduckgo, Bing
	- search_trace_id: 104 cumulTLS features for Google, Bing, Duckduckgo for 
	  the experiment identifying target search engine traces against webpage traces 
	  provided by Panchenko et al.[3]
	3.Feature_selection: extract features evaluated in the paper
	4.Tor-browser-crawler: We used tor-browser-crawlers provided by Juarez et al.[4] and 
	added three parts, typing characters in search box, downloading htmls, and detecting 
	CAPTCHAs. Those additions are reflected in visit.py. Note that to support character 
	typing for different search engines, please modify the following parts of codes with 
	the name of  search engines:
	- For exmaple, for Google, 
		visit.py	
		page = self.tb_driver.get('http://www.google.com')
		
		torutils.py
        domain = get_tld('http://www.google.com')

# References
[1] T. Wang, X. Cai, R. Nithyanand, R. Johnson, and I. Gold-
berg. Effective Attacks and Provable Defenses for Website
Fingerprinting. 23rd USENIX Security Symposium (USENIX
Security 14), pages 143–157, 2014.

[2] J. Hayes and G. Danezis. k-fingerprinting: a Robust Scalable
Website Fingerprinting Technique.

[3] A. Panchenko, F. Lanze, A. Zinnen, M. Henze, J. Pen-
nekamp, K. Wehrle, and T. Engel. Website Fingerprinting
at Internet Scale. 16th NDSS (NDSS 16), pages 143–157,
2016.

[4] M. Juarez, S. Afroz, G. Acar, C. Diaz, and R. Greenstadt. A
Critical Evaluation of Website Fingerprinting Attacks. Pro-
ceedings of the 2014 ACM SIGSAC Conference on Computer
and Communications Security - CCS ’14, pages 263–274,
2014.


