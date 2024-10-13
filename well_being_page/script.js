// Show the next question and hide the current one
document.getElementById('stepOneForm').addEventListener('submit', function (event) {
    event.preventDefault();

    // Hide the basic info form
    document.getElementById('basicInfoForm').classList.add('hidden');

    // Show the first question
    document.getElementById('question1').classList.remove('hidden');

    // Scroll to the top of the page
    window.scrollTo(0, 0);
});

// Navigate from question 1 to question 2
document.getElementById('next1').addEventListener('click', function () {
    document.getElementById('question1').classList.add('hidden');
    document.getElementById('question2').classList.remove('hidden');
    window.scrollTo(0, 0);
});

// Navigate from question 2 to question 3
document.getElementById('next2').addEventListener('click', function () {
    document.getElementById('question2').classList.add('hidden');
    document.getElementById('question3').classList.remove('hidden');
    window.scrollTo(0, 0);
});

document.getElementById('next3').addEventListener('click', function () {
    document.getElementById('question3').classList.add('hidden');
    document.getElementById('question4').classList.remove('hidden');
    window.scrollTo(0, 0);
});

document.getElementById('next4').addEventListener('click', function () {
    document.getElementById('question4').classList.add('hidden');
    document.getElementById('question5').classList.remove('hidden');
    window.scrollTo(0, 0);
});

document.getElementById('next5').addEventListener('click', function () {
    document.getElementById('question5').classList.add('hidden');
    document.getElementById('question6').classList.remove('hidden');
    window.scrollTo(0, 0);
});

document.getElementById('next6').addEventListener('click', function () {
    document.getElementById('question6').classList.add('hidden');
    document.getElementById('question7').classList.remove('hidden');
    window.scrollTo(0, 0);
});

document.getElementById('next7').addEventListener('click', function () {
    document.getElementById('question7').classList.add('hidden');
    document.getElementById('question8').classList.remove('hidden');
    window.scrollTo(0, 0);
});

document.getElementById('next8').addEventListener('click', function () {
    document.getElementById('question8').classList.add('hidden');
    document.getElementById('question9').classList.remove('hidden');
    window.scrollTo(0, 0);
});

// Navigate from question 2 back to question 1
document.getElementById('back2').addEventListener('click', function () {
    document.getElementById('question2').classList.add('hidden');
    document.getElementById('question1').classList.remove('hidden');
    window.scrollTo(0, 0);
});

// Navigate from question 3 back to question 2
document.getElementById('back3').addEventListener('click', function () {
    document.getElementById('question3').classList.add('hidden');
    document.getElementById('question2').classList.remove('hidden');
    window.scrollTo(0, 0);
});

// Submit the survey and show the Thank You page


document.getElementById('submitSurvey').addEventListener('click', function (event) {
    event.preventDefault();  // Prevent the default form submission

    // Hide the survey and show the thank you message
    document.getElementById('question9').classList.add('hidden');  // Hide question 9
    document.getElementById('thankYouPage').classList.remove('hidden');  // Show thank you page

    // Simulate a delay for generating the dashboard (e.g., 3 seconds)
    setTimeout(function () {
        // Hide the thank you page and show the dashboard image
        document.getElementById('thankYouPage').classList.add('hidden');
        document.getElementById('dashboard').classList.remove('hidden');  // Show the dashboard image
    }, 3000);  // 3-second delay for dashboard generation
});




