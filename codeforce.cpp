#include<iostream>
using namespace std;

int main()
{
    int t;
    cin >> t;
    while(t--)
    {
        string s;
        cin >> s;
        
        
        if(s.length()>10)
        {
            int l = s.length();
            cout << s[0] << (l-2) << s[l-1];
        }
        else
        {
            cout << s;
        }
        cout << "hello";
        cout << endl;
    }
}