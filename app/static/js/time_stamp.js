const timeElements = document.getElementsByClassName("time");
const dateElements = document.getElementsByClassName("date");

function formatTimeElement(element) {
  let unixTimeStamp = element.innerText;

  let dateObject = new Date(unixTimeStamp * 1000);

  let hours = "0" + dateObject.getHours();
  let minutes = "0" + dateObject.getMinutes();

  let timeElement = hours.substr(-2) + ":" + minutes.substr(-2);

  element.innerHTML = timeElement;
}

function formatDateElement(element) {
  let unixTimeStamp = element.innerText;

  let dateObject = new Date(unixTimeStamp * 1000);

  let day = "0" + dateObject.getDate();
  let month = "0" + (dateObject.getMonth() + 1);
  let year = dateObject.getFullYear().toString();

  let dateElement =
    day.substr(-2) + "." + month.substr(-2) + "." + year.slice(-2);

  element.innerHTML = dateElement;
}

for (element of timeElements) {
  formatTimeElement(element);
}

for (element of dateElements) {
  formatDateElement(element);
}
