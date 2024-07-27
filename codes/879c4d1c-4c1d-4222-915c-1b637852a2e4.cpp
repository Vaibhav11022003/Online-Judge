#include<bits/stdc++.h>
using namespace std;
int fun(int n)
{
    if(n<=2)return 1;
    return fun(n-1)+fun(n-2);
}
int main()
{
    int n;
    cin>>n;
    int ans=fun(n);
    cout<<ans<<endl;
    return 0;
}