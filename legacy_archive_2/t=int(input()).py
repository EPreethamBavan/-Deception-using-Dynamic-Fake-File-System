t=int(input())
for i in range(t):
    n,q = map(int, input().split())
    a=list(map(int,input().split()))
    b=list(map(int,input().split()))

    for j in range(q):
        l,r = map(int,input().split())
        s=0
        m=0
        ans=[]
        for k in range(n-1,l-2,-1):
           if k<=r-1:
                #print("s",s)
                m=max([m,b[k],a[k]])
                s+=m
           elif k==n-1:
                #print("s2",s)
                m=max(b[k],a[k])    
           elif k>r:
                #print("s3",s)
                m=max([m,b[k],a[k]])
           
        ans.append(s)    
        print(*ans)     
               