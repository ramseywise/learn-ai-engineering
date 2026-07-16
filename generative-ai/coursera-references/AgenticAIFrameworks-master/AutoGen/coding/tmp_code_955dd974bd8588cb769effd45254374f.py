def remove_vowels(s):
    vowels = 'aeiouAEIOU'
    result = ''
    for char in s:
        if char not in vowels:
            result += char
    return result

# Test the function
print(remove_vowels('Hello, World!'))