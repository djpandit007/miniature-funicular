function groupifyOnClick() {
  var groupifyDiv = document.getElementById("groupify-by-div");
  groupifyDiv.innerHTML = `Select Groupify strategy:
                          <br><a href="/similar">Similar Scores</a>
                          <br><a href="dissimilar">Dissimilar Scores</a>`;
}

function pathFindOnClick() {
  var pathDiv = document.getElementById("path-finder-div");
  pathDiv.innerHTML = `<form action="/find-path" method="POST">
                        Select Student from the list:
                        <br><select name="path-student">
                          <option value="1">Alexis Reese</option>
                          <option value="2">Erick	Richards</option>
                          <option value="3">Daryl	Garner</option>
                          <option value="4">Teresa	Tyler</option>
                          <option value="5">Lloyd	Bryant</option>
                          <option value="6">Philip	Gilbert</option>
                          <option value="7">Marian	Chandler</option>
                          <option value="8">Wendy	Craig</option>
                          <option value="9">Alfredo	Soto</option>
                          <option value="10">Archie	Dunn</option>
                          <option value="11">Israel	Banks</option>
                          <option value="12">Heidi	Porter</option>
                          <option value="13">Joanna	Mckenzie</option>
                          <option value="14">Leroy	Boone</option>
                          <option value="15">Michelle	Estrada</option>
                          <option value="16">Mathew	Hernandez</option>
                          <option value="17">Rogelio Quinn</option>
                          <option value="18">Gary	Warren</option>
                          <option value="19">Emily Thornton</option>
                          <option value="20">Billy Parsons</option>
                          <option value="21">Betsy Graves</option>
                        </select>
                        <br><input type="submit" value="Submit">
                        </form>`;
}

function feedbackOnClick() {
  var pathDiv = document.getElementById("progress-div");
  pathDiv.innerHTML = `<form action="/progress" method="POST">
                        Select Student from the list:
                        <br><select name="progress">
                          <option value="1">Alexis Reese</option>
                          <option value="2">Erick	Richards</option>
                          <option value="3">Daryl	Garner</option>
                          <option value="4">Teresa	Tyler</option>
                          <option value="5">Lloyd	Bryant</option>
                          <option value="6">Philip	Gilbert</option>
                          <option value="7">Marian	Chandler</option>
                          <option value="8">Wendy	Craig</option>
                          <option value="9">Alfredo	Soto</option>
                          <option value="10">Archie	Dunn</option>
                          <option value="11">Israel	Banks</option>
                          <option value="12">Heidi	Porter</option>
                          <option value="13">Joanna	Mckenzie</option>
                          <option value="14">Leroy	Boone</option>
                          <option value="15">Michelle	Estrada</option>
                          <option value="16">Mathew	Hernandez</option>
                          <option value="17">Rogelio Quinn</option>
                          <option value="18">Gary	Warren</option>
                          <option value="19">Emily Thornton</option>
                          <option value="20">Billy Parsons</option>
                          <option value="21">Betsy Graves</option>
                        </select>
                        <br><input type="submit" value="Submit">
                        </form>`;
}

function adminOnClick() {
  var pathDiv = document.getElementById("admin-div");
  pathDiv.innerHTML = `<form action="/admin" method="POST">
                        Select Student from the list:
                        <br><select name="admin">
                          <option value="1">Alexis Reese</option>
                          <option value="2">Erick	Richards</option>
                          <option value="3">Daryl	Garner</option>
                          <option value="4">Teresa	Tyler</option>
                          <option value="5">Lloyd	Bryant</option>
                          <option value="6">Philip	Gilbert</option>
                          <option value="7">Marian	Chandler</option>
                          <option value="8">Wendy	Craig</option>
                          <option value="9">Alfredo	Soto</option>
                          <option value="10">Archie	Dunn</option>
                          <option value="11">Israel	Banks</option>
                          <option value="12">Heidi	Porter</option>
                          <option value="13">Joanna	Mckenzie</option>
                          <option value="14">Leroy	Boone</option>
                          <option value="15">Michelle	Estrada</option>
                          <option value="16">Mathew	Hernandez</option>
                          <option value="17">Rogelio Quinn</option>
                          <option value="18">Gary	Warren</option>
                          <option value="19">Emily Thornton</option>
                          <option value="20">Billy Parsons</option>
                          <option value="21">Betsy Graves</option>
                        </select>
                        <br><input type="submit" value="Submit">
                        </form>`;
}
