// form visible
$("#fill_result").on('click', function(){
       // Displaying Rest of the form
       var div_data="<div class='form-group'>";
       div_data+="<label>First Test : </label><input type='text' name='first_test' class='form-control' placeholder='First Test' />";
       div_data+="</div>";

       div_data+="<div class='form-group'>";
       div_data+="<label>Second Test : </label><input type='text' name='second_test' class='form-control' placeholder='Second Test' />";
       div_data+="</div>";

       div_data+="<div class='form-group'>";
       div_data+="<label>Third Test : </label><input type='text' name='third_test' class='form-control' placeholder='Third Test' />";
       div_data+="</div>";

       div_data+="<div class='form-group'>";
       div_data+="<label>Fourth Test : </label><input type='text' name='fourth_test' class='form-control' placeholder='Fourth Test' />";
       div_data+="</div>";


       div_data+="<div class='form-group'>";
       div_data+="<label>Exam Score : </label><input type='text' name='exam_score' class='form-control' placeholder='Exam Score' />";
       div_data+="</div>";

       div_data+="<div class='form-group'>";
       div_data+="<label>Total Score : </label><input type='text' name='total_score' class='form-control' placeholder='Total Score' />";
       div_data+="</div>";

       div_data+="<div class='form-group'>";
       div_data+="<label>Grade : </label><input type='text' name='grade' class='form-control' placeholder='Grade' />";
       div_data+="</div>";

       div_data+="<div class='form-group'>";
       div_data+="<label>Remark : </label><input type='text' name='remark' class='form-control' placeholder='Remark' />";
       div_data+="</div>";

       div_data+="<div class='form-group'>";
       div_data+="<button id='save_result' class='btn btn-success' type='submit'>Save Result</button>";
       div_data+="</div>";
       $("#student_data").html(div_data);

})
