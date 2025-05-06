let user_answer_input = document.getElementById("user_answer_input")
let correct = document.getElementById("correct")
let incorrect = document.getElementById("incorrect")
let country_form = document.getElementById("country_form")
let score = document.getElementById("score")

country_form.addEventListener("submit", check_user_answer)
function check_user_answer(e) {
    e.preventDefault()
    let user_answer_text = user_answer_input.value
    fetch("check_country_answer", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"user_answer_text": user_answer_text})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.result.answer_result === "правильно") {
                alert("Правильно! Плюс 1 балл.")
                correct.innerHTML = Number(correct.innerHTML) + 1
            }
            else if (data.result.answer_result === "близко") {
                alert(`Было близко!\nПравильный ответ: ${data.result.name}\nБаллы не изменятся.`)
            }
            document.getElementById("area_p").innerHTML = data.result.area
            document.getElementById("population_p").innerHTML = data.result.population
            document.getElementById("capital_p").innerHTML = data.result.capital
            document.getElementById("user_answer_input").value = ""
        }
        else {
            alert(`Неправильно.`)
            incorrect.innerHTML = Number(incorrect.innerHTML) + 1
        }
        score.innerHTML = "Баллов: " + (Number(correct.innerHTML) - Number(incorrect.innerHTML))
    })
}

document.getElementById("dont_know").addEventListener("click", () => {
    e.preventDefault()
    fetch("user_dont_know", {
        method: "POST",
        headers: {"Content-Type": "application/json"}
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            incorrect.innerHTML = Number(incorrect.innerHTML) + 1
            document.getElementById("area_p").innerHTML = data.result.area
            document.getElementById("population_p").innerHTML = data.result.population
            document.getElementById("capital_p").innerHTML = data.result.capital
            document.getElementById("user_answer_input").value = ""
        }
        score.innerHTML = "Баллов: " + (Number(correct.innerHTML) - Number(incorrect.innerHTML))
    })
})


