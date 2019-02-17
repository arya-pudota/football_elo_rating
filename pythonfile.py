import csv
#program that uses the ELO rating system to rank football teams
f=open("2017fgr.txt", "r")
g=open("2017fgt.txt", "w")
h=open("2017c.txt", "r")
g.write(h.read())
g.close()
h.close()
footballscores=f.readlines()
#footballscores T1 S1 T2 S2
x=0
for i in footballscores:
    y= ([splits for splits in i.split("\t") if splits is not ""])
    #y in the format [T1, S1, T2, S2]
    g=open("2017fgt.txt", "r+")
    teamscores=g.readlines()
    #teamscores in the format TEAM SCORE
    for j in teamscores:
        if j.split("\t")[0]==y[0]:
            team1=y[0]
            score1=float(j.split("\t")[1].split("\n")[0])
        if j.split("\t")[0]==y[2]:
            team2=y[2]
            score2=float(j.split("\t")[1].split("\n")[0])
        if y[1]>y[3]:
            s1=1
            s2=0
        else:
            s2=1
            s1=0
    r1=10**(score1/400.0)
    r2=10**(score2/400.0)
    e1=r1/(r1+r2)
    e2=r2/(r1+r2)
    k=32.0*(((int(x/9284*116))/116.0)**0.25)
    teamscores.remove(""+team1+"\t"+str(score1)+"\n")
    teamscores.remove(""+team2+"\t"+str(score2)+"\n")
    score1=score1+k*(s1-e1)
    score2=score2+k*(s2-e2)
    teamscores.append(""+team1+"\t"+str(score1)+"\n")
    teamscores.append(""+team2+"\t"+str(score2)+"\n")
    g.close()
    g=open("2017fgt.txt", "w")
    g.writelines(teamscores)
    g.close()
    x=x+1
    if x % 1000 == 0:
        print(x)
    if x==9284:
        break
print("Done")

with open("football_rankings.csv", mode='w') as f_rankings:
    f_write = csv.writer(f_rankings, delimiter = ',', quotechar = '"', quoting=csv.QUOTE_MINIMAL)
    for i in teamscores:
        z = i.split("\t")
        z[0].lstrip()
        z[1] = z[1].rstrip("\n")
        print(z)
        f_write.writerow(z)
    
    
    

    
    
    
            
    
    
            
        
        
        
            
        
    
