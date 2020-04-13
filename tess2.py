import cv2 
import pytesseract
from pytesseract import Output
import re
import csv
import scrython
import time

def listToString(s):  
    
    # initialize an empty string 
    str1 = ""  
    
    # traverse in the string   
    for ele in s:  
        str1 += ele   
    
    # return string   
    return str1  

def psmChange(img, psmNum):

    # Adding custom options
    custom_config = r'--oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzQWERTYUIOPLKJHGFDSAZXCVBNM\' --psm ' + str(psmNum)
    text = pytesseract.image_to_string(img, config=custom_config)


    # write data in a file. 
    #file1 = open("names" + str(psmNum) + ".txt","w") 
    #file1.writelines(text) 
    #file1.close() #to change file access modes    

    #Make a list seperated on newlines and what not
    textlist = re.findall(r'\S+|\n',text)

    #Removes weird wrong words
    for x in range(len(textlist)): 
        if len(textlist[x]) <= 2 and textlist[x] != "\n":
            textlist[x] = " 0 "
        elif textlist[x].islower():
            textlist[x] = " 0 "
        elif len(re.findall(r'[A-Z]',textlist[x])) >= len(textlist[x]) - 2 or len(re.findall(r'[A-Z]',textlist[x])) >= len(textlist[x])*0.3:
            textlist[x] = " 0 "

    textlist = [x for x in textlist if x != " 0 "]
    textlist = [x for x in textlist if x != "\n"]


    ##Adds spaces to names of cards
    for x in range(len(textlist)):
        spaceCheck = list(textlist[x])
        i = 0;
        while i < len(spaceCheck):
            if i == 0 and spaceCheck[i].islower():
                spaceCheck[i] = ""
                i += 1
            elif spaceCheck[i].isupper() and i != 0:
                spaceCheck.insert(i, ' ')
                i += 1
            i += 1
        textlist[x] = listToString(spaceCheck)


    ##GRABS PRICES FOR THE CARDS
    pricelist = []
    print('in price check')
    for x in range(len(textlist)):
        cardname = str(textlist[x])
        try:
            time.sleep(0.1)
            card = scrython.cards.Named(fuzzy=cardname)
            pricelist.append(card.prices('usd'))
        except:
            pricelist.append('error in card name')
    print('done price check')

    return textlist, pricelist;



img = cv2.imread('20200410_212316.jpg')
csvfile = 'output.csv'
bestPrices = 0;
bestPSM = 0;

for x in range(6,13):
    q,p = psmChange(img, x)
    count = 0;
    for i in range(len(p)):
        if (p[i] == 'error in card name'):
            count += 1
    if (len(p) - count > bestPrices):
        bestPSM = x
        bestPrices = len(p) - count

q,p = psmChange(img,bestPSM)


# Write data to file
with open(csvfile, 'w', newline='') as csvfile:
    fieldnames = ['Card Name', 'Card Price']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for i, j in zip(q, p):
        writer.writerow({'Card Name': i, 'Card Price': j})

print(bestPrices)

cv2.waitKey(0)