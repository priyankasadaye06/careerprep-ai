const templateFields = {
    template1: `
        <h3>Summary</h3>
        <textarea name="summary"></textarea>

        <h3>Experience</h3>
        <textarea name="experience"></textarea>
    `,

    template2: `
        <h3>Key Achievements</h3>
        <textarea name="key_achievements"></textarea>
    `,

    template3: `
        <h3>Projects</h3>
        <textarea name="projects"></textarea>

        <input name="gpa" placeholder="GPA">
    `,

    template4: `
        <h3>Expertise</h3>
        <textarea name="expertise"></textarea>
    `,

    template5: `
        <h3>Creative Profile</h3>
        <textarea name="creative_summary"></textarea>
    `
};

const roleFields = {
    "Software Engineer": `
        <h3>Tech Stack</h3>
        <textarea name="tech_stack"></textarea>

        <h3>System Design</h3>
        <textarea name="system_design"></textarea>
    `,

    "Data Analyst": `
        <h3>Tools</h3>
        <textarea name="tools"></textarea>

        <h3>KPIs / Dashboards</h3>
        <textarea name="dashboards"></textarea>
    `,

    "ML Engineer": `
        <h3>ML Models</h3>
        <textarea name="ml_models"></textarea>

        <h3>Deployment</h3>
        <textarea name="deployment"></textarea>
    `
};

const container = document.getElementById("dynamicFields");

let html = "";

// Template-based fields
if (templateFields[selectedTemplate]) {
    html += templateFields[selectedTemplate];
}

// Role-based fields
if (roleFields[selectedRole]) {
    html += `<hr>${roleFields[selectedRole]}`;
}

container.innerHTML = html;