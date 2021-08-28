#ifndef JW_DIST

#include <iostream>
#include <algorithm>
#define JW_DIST

float jw_distance(std::string s1, std::string s2, bool caseSensitive = true)
{
    float m = 0;
    int low, high, range;
    int k = 0, numTrans = 0;

    // Exit early if either are empty
    if (s1.length() == 0 || s2.length() == 0)    
{
        return 0;
    }

    // Convert to lower if case-sensitive is false
    if (caseSensitive == false)    
{
        transform(s1.begin(), s1.end(), s1.begin(), ::tolower);
        transform(s2.begin(), s2.end(), s2.begin(), ::tolower);
    }

    // Exit early if they're an exact match.
    if (s1 == s2)    
{
        return 1;
    }

    range = (std::max(s1.length(), s2.length()) / 2) - 1;
    int s1Matches[s1.length()];
    int s2Matches[s2.length()];

    for (int i = 0; i < s1.length(); i++)
    {

        // Low Value;
        if (i >= range)        
{
            low = i - range;
        }
        else
        {
            low = 0;
        }

        // High Value;
        if (i + range <= (s2.length() - 1))        
{
            high = i + range;
        }
        else
        {
            high = s2.length() - 1;
        }

        for (int j = low; j <= high; j++)        
{
            if (s1Matches[i] != 1 && s2Matches[j] != 1 && s1[i] == s2[j])
            {
                m += 1;
                s1Matches[i] = 1;
                s2Matches[j] = 1;
                break;
            }
        }
    }

    // Exit early if no matches were found
    if (m == 0)    
{
        return 0;
    }

    // Count the transpositions.
    for (int i = 0; i < s1.length(); i++)    
{
        if (s1Matches[i] == 1)        
{
            int j;
            for (j = k; j < s2.length(); j++)            
{
                if (s2Matches[j] == 1)                
{
                    k = j + 1;
                    break;
                }
            }

            if (s1[i] != s2[j])            
{
                numTrans += 1;
            }
        }
    }

    float weight = (m / s1.length() + m / s2.length() + (m - (numTrans / 2)) / m) / 3;
    float l = 0;
    float p = 0.1;
    if (weight > 0.7)    
{
        while (s1[l] == s2[l] && l < 4)        
{
            l += 1;
        }

        weight += l * p * (1 - weight);
    }
    return weight;
}

#endif
