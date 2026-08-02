function formatDOB(input){

    let value = input.value.replace(/\D/g, "");

    if(value.length > 8){
        value = value.substring(0,8);
    }

    let formatted = "";

    if(value.length > 0){
        formatted = value.substring(0,2);
    }

    if(value.length >= 3){
        formatted += "/" + value.substring(2,4);
    }

    if(value.length >= 5){
        formatted += "/" + value.substring(4,8);
    }

    input.value = formatted;

    calculateAge();

}



function calculateAge(){

    let dob = document.getElementById("dob").value;


    if(dob){

        let parts = dob.split("/");


        if(parts.length === 3 && parts[2].length === 4){

            let birthDate = new Date(
                parts[2],
                parts[1] - 1,
                parts[0]
            );


            let today = new Date();


            let age = today.getFullYear() - birthDate.getFullYear();


            let monthDifference = today.getMonth() - birthDate.getMonth();


            if(
                monthDifference < 0 ||
                (monthDifference === 0 && today.getDate() < birthDate.getDate())
            ){
                age--;
            }


            document.getElementById("age").value = age;

        }

    }
    else{

        document.getElementById("age").value = "";

    }

}
