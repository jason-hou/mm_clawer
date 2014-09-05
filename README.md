mm_clawer
=========

fetch image from specified webpage

update history:

1. Use BeautifulSoup to parse url, then fetch all image links;
use urllib.urlretrieve to download it respectively in single threading;

2. Use multiprocessing.dummy.Pool().map to download image in multi-threading;
Refer to "Parallelism in one line":(link:
https://medium.com/@thechriskiehl/parallelism-in-one-line-40e9b2b36148involve)

3. To achieve target that support download specified amount picture, the whole 
threading need to synchronize, that is, a counter like is a must. 
Use threading.Thread and threading.lock(as mutex) to instead of multiprocess;

4. Involve argparse to support command line arguments, such as:
    -n number of threading, default to 10
    -o output path to save images, default to 'pics'
    -l limit of the max amount of images, default to no limit
   Create Clawer class instead of functions; 

5. To support more image website(especially nonEnglish website), It's a must to 
handle different charset, such as gb2312, gbk and so on. I choose to solve the 
unicode issue in BeautifulSoup way -- detect original encoding, then decode the 
content to unicode.

6. To improve the url access speed, use add_header('Accept-encoding', 'gzip') to
inform the web serve to fetch compressed data, then use gzip and StringIO to 
uncompress the data.
   Use pep8 style to format the whole script;
   
7. Try to use directly file operation method instead of urllib.urlretrieve as 
download method.(revert later)

8. Research the recursion in python web crawler, fetch the whole available links
 to other image page in depth recursion(default 0).
 
9. Currently It's the bottleneck to parse each url in deep recursion. 
Study multi-threading of multiprocess to solve the bottleneck when recursion 
depth is not default...

10. Reduce the time cost on parsing urls recursively.

11. Handle htm url.
 
