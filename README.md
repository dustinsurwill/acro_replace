# acro_replace

## Description
Python 3 utility to mimic the autocorrect (autoexpand) functions of WordPerfect. This program will replace any words you define with word(s) or phrase on punctuation key_down.

## Punctuation
List of punctuation the program will trigger on:
- space
- period ( . )
- comma ( , )
- question mark ( ? )
- exclamation mark ( ! )
- dash ( - )
- underscore ( _ )
- closing parenthesis ( ) )
- colon ( : )
- semicolon ( ; )
- double quote ( " )

## How to use

1. In order to make it work download the latest version: https://github.com/falconraptor/acro_replace/releases
    1. Might have to click the arrow then `Keep` if using Chrome
2. Put the file wherever you want
3. Run the program
    1. If windows protects your PC click `More Info` then `Run Anyway`
4. In the notification tray (the place with the clock and battery icons in the bottom right corner)
    1. Find the generic icon that says `Text Replace`, it may be hidden in the expanded area (click the up arrow to show that area)
    2. Right click on the icon, then click `Open Config`
5. In the file that opens, put the text you want to replace comma the text you want it to replace with. Separate the different replacements with a newline (enter key)
    1. example:
        ```
        teh,the
        adn,and
        awnser,anwser
        ```
    2. The word you want to replace cannot include any of the [punctuation specified above](#punctuation)
6. Save and close the file
7. In the notification tray (the place with the clock and battery icons in the bottom right corner)
    1. Find the generic icon that says `Text Replace`, it may be hidden in the expanded area (click the up arrow to show that area)
    2. Right click on the icon, then click `Reload Config`
8. Enjoy the automatic replacement of text whenever you type one of the [punctuation specified above](#punctuation)
    1. In order to add, remove, modify any of the replacements follow steps 4-7
