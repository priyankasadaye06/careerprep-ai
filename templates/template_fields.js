<script>
const templateFields = {
  template1: `
    <textarea name="summary" placeholder="Professional Summary"></textarea>
    <textarea name="experience" placeholder="Experience"></textarea>
  `,

  template2: `
    <input type="file" name="photo">
    <textarea name="key_achievements"></textarea>
  `,

  template3: `
    <textarea name="projects"></textarea>
    <input name="gpa" placeholder="GPA">
  `
};

document.getElementById("templateSelect").addEventListener("change", updateFields);
document.getElementById("roleSelect").addEventListener("change", updateFields);

function updateFields() {
  const template = document.getElementById("templateSelect").value;
  const role = document.getElementById("roleSelect").value;

  let html = "";

  if (templateFields[template]) {
    html += templateFields[template];
  }

  if (roleFields[role]) {
    html += roleFields[role];
  }

  document.getElementById("dynamicFields").innerHTML = html;
}
</script>