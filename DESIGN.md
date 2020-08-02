    This program is broken down into several functions which each render a particular html file and serve a particular function. The first function is called home,
and it is called whenever the user goes to the url ending in "/". Home takes two methods: "GET" and "POST". When the method is "GET" (the default), the function
renders the home.html file, which displays the homepage described in README.md. However, before rendering the HTML file, it checks if the key 'editable' exists in
the dictionary session. If it does not, it creates a key called 'editable' whose value is an empty array. This is done so that later on, when the program checks if
a file is contained in session['editable] (meaning that the user has access to edit the document), they will not receive an error that session['editable'] does not
exist.
    home.html is titled "Homepage". In the main block of the file is a list of options where the user can choose one (radios). Their names are all "category" so that
they can be called in the home function. There is also a button called next to allow the user to submit their category choice.
    Once the next button is pressed, home is called with the "POST" method instead of the "GET" method. The name of the chosen category is stored in the session
dictionary with a kay of 'category'. The function then directs the user to the "/directory" page, which calls the directory function.
    The directory function also has two methods: "GET" and "POST". When the method is "POST", all the names of documents whose category matches the pre-selected
category are selected into a variable called documents. Since document names have a .txt ending, the function loops through documents and removes the last four
characters from the file names. It then renders directory.html with a variable called documents set to documents.
    directory.html is titled "Directory". It checks if documents is empty. If it is, it display only a link called "new" that, when clicked, enables the user to
create a new document. However, when documents is not empty, it displays a form with radios for each line in documents. Since the value should match the SQL table,
the value has the name stored in documents plus ".txt" appended to its end. At the end of the form is a button called "Read" that submits the chosen file. Once
pressed, the directory function is called with the "POST" method.
    When called with the "POST" method, the directory function stores the name of the text file in the session dictionary with a key of 'name'. It then selects the
password from the SQL table for the file whose name matches the selected name. If the password is empty (i.e. is matches ""), check_password_hash returns True.
When this occurs the program checks if the name of the file already exists in the array of the user's editable files stored in session with the key 'editable'. If
it is not, the file name is added to the list. Regardless of whether or not the password exists, the program redirects the user to the "/document" page.
    As mentioned above, instead of choosing an existing document, the user can click on "new" to create their own document. Clicking on "new" directs the user to
"/new". When the new function is called, its default method is "GET", which simply renders new.html. new.html is a form with two text inputs: a file name and an
optional password. Once the user clicks "Create" the new function is called with the "POST" method.
    When the method is "POST", the new function first sets session['name'] equal to the inputted file name and then appends ".txt" to the end of it. It then assigns
a variable called current equal to the selection of all entries in the SQL table with the same name. If the length of current is greater than an apology is returned
explaining that that name is already in use. Otherwise, the variable password is set to whatever was inputted as the password. Then, the name of the file is added to
session['editable'], the list of files that the user can edit. Then, the new file is added to the SQL table of documents. It takes the name of the file, a hash of
the password, the category it fits into (stored in session['category']), and the date and time it was created. This last piece of information is helpful for
ordering the entries in the directory from newest to oldest. Finally, the actual file is created, and the user is directed to "/document".
    When the user goes to "/document", the document function is called. With its default "GET" mode, the function opens the file stored in session['name'] in
read mode. It then checks if the user can edit the document by checking if the file name is in session['editable']. If it is, document.html is rendered with a
variable called document set to the read file and a variable called editable set to true. If the file name is not contained in session['editable'], the same
thing is rendered but where editable equals False.
    document.html is titled "Document". It checks if editable is True. If it is, it displays the contents of the chosen file in a textarea which is editable. It
also has a button called save to submit any changes made to the document. If editable is not True, the same thing is displayed except that the textarea is view
only and the button says "edit" instead of save. Once the button is pressed, the document function is called with the "POST" method.
    When the document function is called with a "POST" method, the function first checks if the file name is in session['editable']. If it is, it means that the
save button was clicked. Therefore, it opens the file in append mode and truncates it to a size of 0 bytes, meaning that it erases all of the file's contents.
The function then closes the file and reopens it in write mode. It then writes the contents of the textarea to the file and redirects to /document so that the
user can continue to read and edit their document. However, if the file name was not in session['editable'], it directs the user to "/login".
    When the login function is called in its default "GET" method, it simply returns login.html. login.html prompts the user for a password and has a submit
button to submit the password. Once submitted, login is called with the "POST" method. The function first sets a variable called password equal to the user's
input for the password. It then assigns the check variable to the password of the entry in the SQL table whose file name is equal to session['name']. The function
then calls check_password_hash to see if the user inputted the correct password. If it returns True, the file name is added to session['editable'] and then the
user is directed back to "/document". If the password is incorrect, however, an apology is returned stating that the password was incorrect.
