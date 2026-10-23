"""Contenido inicial. Formato de cada línea: ver datos en VERBOS / VOCABULARIO.

Verbos: infinitivo | español | 3.ª persona | pasado | participio  (regulares marcados con REGULARES)
Vocabulario: inglés | español
"""

VERBOS_IRREGULARES = """
be|ser / estar|is|was / were|been
go|ir|goes|went|gone
eat|comer|eats|ate|eaten
have|tener|has|had|had
do|hacer|does|did|done
make|hacer / fabricar|makes|made|made
take|tomar / llevar|takes|took|taken
see|ver|sees|saw|seen
come|venir|comes|came|come
give|dar|gives|gave|given
get|conseguir / obtener|gets|got|got
know|saber / conocer|knows|knew|known
think|pensar|thinks|thought|thought
buy|comprar|buys|bought|bought
write|escribir|writes|wrote|written
read|leer|reads|read|read
speak|hablar|speaks|spoke|spoken
drink|beber|drinks|drank|drunk
sleep|dormir|sleeps|slept|slept
run|correr|runs|ran|run
say|decir|says|said|said
tell|contar / decir|tells|told|told
find|encontrar|finds|found|found
leave|salir / dejar|leaves|left|left
meet|conocer / encontrarse|meets|met|met
pay|pagar|pays|paid|paid
sit|sentarse|sits|sat|sat
sing|cantar|sings|sang|sung
swim|nadar|swims|swam|swum
drive|conducir|drives|drove|driven
bring|traer|brings|brought|brought
begin|empezar|begins|began|begun
understand|entender|understands|understood|understood
forget|olvidar|forgets|forgot|forgotten
wear|usar (ropa)|wears|wore|worn
lose|perder|loses|lost|lost
feel|sentir|feels|felt|felt
""".strip()

VERBOS_REGULARES = """
work|trabajar|works|worked
play|jugar / tocar|plays|played
study|estudiar|studies|studied
live|vivir|lives|lived
like|gustar|likes|liked
want|querer|wants|wanted
need|necesitar|needs|needed
watch|mirar|watches|watched
help|ayudar|helps|helped
call|llamar|calls|called
walk|caminar|walks|walked
cook|cocinar|cooks|cooked
clean|limpiar|cleans|cleaned
open|abrir|opens|opened
close|cerrar|closes|closed
learn|aprender|learns|learned
listen|escuchar|listens|listened
talk|conversar|talks|talked
wait|esperar|waits|waited
ask|preguntar / pedir|asks|asked
use|usar|uses|used
love|amar|loves|loved
visit|visitar|visits|visited
travel|viajar|travels|traveled
""".strip()

# (nombre, slug, palabras)
VOCABULARIO = [
    ('Saludos y cortesía', 'saludos', """
hello|hola
goodbye|adiós
good morning|buenos días
good afternoon|buenas tardes
good night|buenas noches
please|por favor
thank you|gracias
sorry|perdón
excuse me|disculpe
welcome|bienvenido
yes|sí
no|no
""".strip()),
    ('Casa', 'casa', """
house|casa
room|habitación
kitchen|cocina
bathroom|baño
bed|cama
table|mesa
chair|silla
door|puerta
window|ventana
floor|piso
wall|pared
roof|techo
""".strip()),
    ('Comida y bebida', 'comida', """
water|agua
bread|pan
milk|leche
coffee|café
rice|arroz
meat|carne
chicken|pollo
fish|pescado
fruit|fruta
apple|manzana
egg|huevo
cheese|queso
""".strip()),
    ('Familia', 'familia', """
mother|madre
father|padre
sister|hermana
brother|hermano
son|hijo
daughter|hija
grandmother|abuela
grandfather|abuelo
uncle|tío
aunt|tía
cousin|primo / prima
friend|amigo
""".strip()),
    ('Trabajo y estudio', 'trabajo', """
job|trabajo
office|oficina
boss|jefe
meeting|reunión
computer|computador
school|escuela
teacher|profesor
student|estudiante
book|libro
homework|tarea
exam|examen
salary|salario
""".strip()),
    ('Transporte y lugares', 'lugares', """
car|carro
bus|bus
train|tren
airplane|avión
bicycle|bicicleta
street|calle
city|ciudad
store|tienda
hospital|hospital
bank|banco
park|parque
airport|aeropuerto
""".strip()),
    ('Tiempo y números', 'tiempo', """
today|hoy
tomorrow|mañana
yesterday|ayer
week|semana
month|mes
year|año
Monday|lunes
Tuesday|martes
Wednesday|miércoles
Thursday|jueves
Friday|viernes
Saturday|sábado
Sunday|domingo
one|uno
two|dos
three|tres
four|cuatro
five|cinco
ten|diez
hundred|cien
""".strip()),
    ('Cuerpo y salud', 'cuerpo', """
head|cabeza
hand|mano
foot|pie
eye|ojo
mouth|boca
arm|brazo
leg|pierna
stomach|estómago
doctor|médico
medicine|medicina
pain|dolor
sick|enfermo
""".strip()),
    ('Ropa y colores', 'ropa', """
shirt|camisa
pants|pantalones
shoes|zapatos
dress|vestido
hat|sombrero
jacket|chaqueta
red|rojo
blue|azul
green|verde
yellow|amarillo
black|negro
white|blanco
""".strip()),
]
