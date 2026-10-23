"""Inglés para la industria del software.

Formato por línea: inglés|español|oración de ejemplo
"""

TECNICO = [
    ('Dev: código y conceptos', 'dev-codigo', """
variable|variable|I declared a variable to store the user name.
function|función|This function returns the total price.
method|método|Call the method after you create the object.
class|clase|Each class has its own properties.
loop|bucle|The loop runs until the list is empty.
array|arreglo|The array contains five elements.
string|cadena de texto|Convert the number to a string.
object|objeto|The object has two properties.
parameter|parámetro|The function takes two parameters.
argument|argumento|Pass the user ID as an argument.
return value|valor de retorno|The return value is null when nothing is found.
bug|error de software|I found a bug in the login page.
exception|excepción|The code throws an exception when the file is missing.
compile|compilar|It takes a minute to compile the project.
debug|depurar|I need to debug this function.
deploy|desplegar|We deploy the app every Friday.
framework|framework|Django is a Python framework.
library|librería|We use a library to parse dates.
dependency|dependencia|Update the dependency to the latest version.
endpoint|punto de acceso de una API|The endpoint returns a list of users.
database|base de datos|The database stores all the orders.
query|consulta|This query is too slow.
schema|esquema|We changed the database schema.
server|servidor|The server is down.
client|cliente|The client sends a request to the server.
request|solicitud|The request failed with a timeout.
response|respuesta de un servidor|The response contains the user data.
frontend|interfaz del usuario (frontend)|She works on the frontend.
backend|lógica del servidor (backend)|He is a backend developer.
cache|caché|Clear the cache and try again.
thread|hilo de ejecución|Each task runs in its own thread.
algorithm|algoritmo|We need a faster algorithm.
syntax|sintaxis|There is a syntax error on line ten.
runtime|tiempo de ejecución|The error happens at runtime.
interface|interfaz de código|The class implements the interface.
module|módulo|Import the module at the top of the file.
script|script|I wrote a script to automate the backup.
feature|funcionalidad|We are building a new feature.
refactor|refactorizar|Let's refactor this code before adding more.
legacy code|código heredado|We still maintain some legacy code.
workaround|solución temporal|This is just a workaround, not a real fix.
default value|valor por defecto|The default value is zero.
null|nulo|The field cannot be null.
timeout|tiempo de espera agotado|The request hit a timeout.
""".strip()),
    ('Dev: Git y code review', 'dev-git', """
repository|repositorio|Clone the repository to your machine.
commit|confirmar cambios (commit)|Make a small commit with a clear message.
branch|rama|Create a new branch for this task.
merge|fusionar|We merge the branch after the review.
merge conflict|conflicto de fusión|I have a merge conflict in two files.
pull request|solicitud de cambios (PR)|I opened a pull request for the login fix.
code review|revisión de código|Can you do a code review for me?
approve|aprobar|She approved the pull request.
rebase|reorganizar commits (rebase)|Rebase your branch on main.
push|subir cambios|Push your changes to the remote.
pull|traer cambios|Pull the latest changes before you start.
clone|clonar|Clone the repo first.
fork|bifurcar un proyecto (fork)|I forked the project on GitHub.
diff|diferencias entre versiones|Check the diff before you commit.
revert|revertir|We had to revert that commit.
tag|etiqueta de versión|We created a tag for version two.
release|lanzamiento|The release is scheduled for Monday.
patch|parche|We shipped a patch for the security issue.
hotfix|corrección urgente|We need a hotfix in production.
squash|combinar commits (squash)|Squash the commits before merging.
stash|guardar cambios temporalmente|I stashed my changes to switch branches.
cherry-pick|copiar un commit específico|I cherry-picked the fix into the release branch.
nitpick|detalle menor|Just a nitpick: rename this variable.
blocker|comentario bloqueante|This comment is a blocker.
suggestion|sugerencia|I left a suggestion on line twenty.
LGTM|me parece bien (looks good to me)|LGTM, ready to merge.
feedback|retroalimentación|Thanks for the feedback.
outdated|desactualizado|This branch is outdated.
conflict|conflicto|Resolve the conflict and push again.
changelog|registro de cambios|Add this to the changelog.
""".strip()),
    ('Dev: equipo y metodologías ágiles', 'dev-agil', """
sprint|ciclo de trabajo (sprint)|Our sprint ends on Friday.
backlog|lista de pendientes (backlog)|We have too many items in the backlog.
standup|reunión diaria|I will give an update at the standup.
retrospective|retrospectiva|In the retrospective we talked about what went wrong.
user story|historia de usuario|Each user story has acceptance criteria.
ticket|tarea registrada (ticket)|I created a ticket for this bug.
task|tarea|This task is almost done.
estimate|estimar|Can you estimate how long it will take?
deadline|fecha límite|The deadline is next Tuesday.
milestone|hito|We reached an important milestone.
roadmap|hoja de ruta|The roadmap includes three new features.
stakeholder|parte interesada|We need to inform the stakeholders.
requirement|requisito|The client changed the requirements again.
scope|alcance|That is outside the scope of this project.
priority|prioridad|This bug is high priority.
velocity|velocidad del equipo|Our velocity went up this sprint.
product owner|responsable del producto|The product owner decides the priorities.
scrum master|facilitador de scrum|The scrum master runs the meetings.
sprint planning|planificación del sprint|Sprint planning is on Monday morning.
demo|demostración|We will give a demo to the client.
handoff|traspaso|We need a clean handoff to the support team.
onboarding|incorporación de personal|Her onboarding starts next week.
pair programming|programación en pareja|We did pair programming to solve it.
technical debt|deuda técnica|Technical debt slows us down.
bottleneck|cuello de botella|The review process is a bottleneck.
blocked|bloqueado|I am blocked by the API team.
on track|en buen camino|The project is on track.
behind schedule|retrasado|We are two days behind schedule.
ownership|responsabilidad sobre algo|Take ownership of this module.
workload|carga de trabajo|My workload is too high this week.
""".strip()),
    ('Dev: reuniones y comunicación', 'dev-reuniones', """
agenda|agenda|Let's check the agenda first.
follow-up|seguimiento|I will send a follow-up email.
action item|tarea acordada|The action items are in the notes.
takeaway|conclusión principal|The main takeaway is to test earlier.
update|actualización|Here is a quick update on the project.
availability|disponibilidad|What is your availability tomorrow?
on call|de guardia|I am on call this weekend.
out of office|fuera de la oficina|She is out of office until Monday.
heads up|aviso previo|Just a heads up: the server will restart.
bandwidth|capacidad de tiempo|I do not have the bandwidth for this now.
sync|reunión de sincronización|Let's have a quick sync tomorrow.
ping|escribir un mensaje rápido|Ping me if you need help.
asynchronous|asíncrono|We prefer asynchronous communication.
remote|remoto|Our team works remotely.
time zone|zona horaria|We are in different time zones.
reschedule|reprogramar|Can we reschedule the meeting?
clarify|aclarar|Can you clarify the requirement?
elaborate|explicar con más detalle|Could you elaborate on that?
share my screen|compartir mi pantalla|Let me share my screen.
mute|silenciar|You are on mute.
raise a concern|expresar una preocupación|I want to raise a concern about the deadline.
make sure|asegurarse|Make sure everyone has access.
keep me posted|mantenme informado|Keep me posted on the progress.
touch base|ponerse en contacto|Let's touch base next week.
wrap up|terminar|Let's wrap up the meeting.
""".strip()),
    ('Dev: entrevistas y carrera', 'dev-carrera', """
resume|currículum|Please send me your resume.
cover letter|carta de presentación|I wrote a short cover letter.
interview|entrevista|I have an interview on Thursday.
recruiter|reclutador|The recruiter called me yesterday.
hiring manager|gerente de contratación|The hiring manager asked about my projects.
job offer|oferta de trabajo|I received a job offer.
salary|salario|What is the salary range?
benefits|beneficios laborales|The benefits include health insurance.
notice period|período de preaviso|My notice period is two weeks.
strength|fortaleza|One of my strengths is communication.
weakness|debilidad|My weakness is public speaking.
portfolio|portafolio|You can see my work in my portfolio.
whiteboard|pizarra|They asked me to solve a problem on the whiteboard.
coding challenge|reto de programación|I completed the coding challenge.
take-home test|prueba para hacer en casa|The take-home test took four hours.
technical interview|entrevista técnica|The technical interview was difficult.
behavioral question|pregunta de comportamiento|Tell me about a time you failed is a behavioral question.
reference|referencia laboral|I can provide two references.
promotion|ascenso|She got a promotion last month.
raise|aumento de sueldo|I asked for a raise.
junior|principiante (junior)|He is a junior developer.
senior|con experiencia (senior)|She is a senior engineer.
freelance|trabajo independiente|I work as a freelance developer.
full-time|tiempo completo|It is a full-time position.
part-time|medio tiempo|I am looking for a part-time job.
""".strip()),
    ('Dev: incidentes y operaciones', 'dev-ops', """
incident|incidente|We had an incident last night.
outage|caída del servicio|The outage lasted two hours.
downtime|tiempo fuera de servicio|We need to reduce downtime.
root cause|causa raíz|We found the root cause of the problem.
rollback|reversión a una versión anterior|We did a rollback to the previous version.
monitoring|monitoreo|Monitoring showed a spike in errors.
alert|alerta|An alert woke me up at three in the morning.
logs|registros del sistema|Check the logs for errors.
latency|latencia|The latency is higher than usual.
uptime|tiempo de disponibilidad|We guarantee ninety-nine percent uptime.
scale|escalar|We need to scale the servers.
load balancer|balanceador de carga|The load balancer sends traffic to three servers.
container|contenedor|The app runs in a container.
pipeline|flujo de integración (pipeline)|The pipeline failed on the tests.
environment|entorno|Do not test in the production environment.
production|producción|The bug only happens in production.
staging|entorno previo a producción (staging)|Deploy to staging first.
configuration|configuración|The configuration file is missing.
migration|migración|Run the database migration.
backup|copia de seguridad|We take a backup every night.
vulnerability|vulnerabilidad|They found a security vulnerability.
postmortem|análisis posterior al incidente|We wrote a postmortem after the outage.
fail over|conmutar al sistema de respaldo|The system will fail over to the backup.
throttle|limitar la velocidad|We throttle requests to protect the API.
memory leak|fuga de memoria|There is a memory leak in the service.
""".strip()),
]
