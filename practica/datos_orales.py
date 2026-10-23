"""Preguntas para práctica oral.

Cada una: (tema, pregunta, traducción, estructura sugerida, respuesta modelo, frases útiles separadas por |)
Las respuestas modelo son ejemplos para comparar, no para memorizar: cambia los datos por los tuyos.
"""

PREGUNTAS_ORALES = [
    # ------------------------------------------------------------ entrevista
    ('entrevista', 'Tell me about yourself.', 'Cuéntame sobre ti.',
     'Presente (quién eres) → pasado (experiencia) → futuro (qué buscas). 60 a 90 segundos.',
     "I am a backend developer with four years of experience. I started in a small company, where I built "
     "internal tools, and later I worked on a payment platform used by thousands of people. Now I am looking "
     "for a team where I can grow and work on larger systems.",
     'I am a ... developer|I have ... years of experience|I have worked on|I am looking for a team where'),
    ('entrevista', 'Why do you want to work here?', '¿Por qué quieres trabajar aquí?',
     'Algo concreto de la empresa → cómo encaja con tu experiencia → qué aportarías.',
     "I like that your product helps small businesses, and I have worked on similar problems before. "
     "I think my experience with APIs would help the team, and I would also learn a lot from your engineers.",
     'I am interested in|I admire|My experience fits|I could contribute by'),
    ('entrevista', 'What is your biggest strength?', '¿Cuál es tu mayor fortaleza?',
     'Una fortaleza → un ejemplo corto → el resultado.',
     "My biggest strength is communication. In my last project, I explained technical problems to the "
     "business team in simple words, and that helped us avoid two big misunderstandings.",
     'One of my strengths is|For example|As a result|That helped us'),
    ('entrevista', 'What is your biggest weakness?', '¿Cuál es tu mayor debilidad?',
     'Una debilidad real y pequeña → qué haces para mejorarla.',
     "I used to take too many tasks at the same time. Now I plan my week every Monday and I say no, or I ask "
     "for more time, when I am already full.",
     'I used to|I am working on|Now I|To improve this, I'),
    ('entrevista', 'Tell me about a time you failed.', 'Cuéntame de una vez que fallaste.',
     'Situación → qué falló → qué aprendiste → qué cambiaste (método STAR).',
     "Once I deployed a change without enough tests, and it broke the checkout page for an hour. "
     "I helped roll it back, and then I wrote a postmortem. After that, we added automated tests to the pipeline.",
     'Once I|It went wrong because|I learned that|After that, we'),
    ('entrevista', 'Tell me about a conflict with a teammate.', 'Cuéntame de un conflicto con un compañero.',
     'Contexto sin culpar → qué hiciste para hablarlo → resultado.',
     "A teammate and I disagreed about the design of an API. I asked for a short call, we listed the pros and "
     "cons of each option, and we chose a middle solution. We still work well together.",
     'We disagreed about|I suggested|We agreed to|In the end'),
    ('entrevista', 'Where do you see yourself in five years?', '¿Dónde te ves en cinco años?',
     'Habilidades que quieres tener → tipo de rol → conexión con la empresa.',
     "In five years, I would like to be a senior engineer who can design systems and help other developers "
     "grow. I also want to understand the business better.",
     'I would like to|I see myself as|I want to keep learning'),
    ('entrevista', 'Why are you leaving your current job?', '¿Por qué dejas tu trabajo actual?',
     'Positivo y honesto: lo que buscas, sin hablar mal de nadie.',
     "I have learned a lot in my current job, but I am looking for new challenges and more responsibility. "
     "I want to work with a larger team and with modern tools.",
     'I am looking for|I want to grow|I have learned a lot'),
    ('entrevista', 'Describe a challenging project you worked on.', 'Describe un proyecto desafiante en el que trabajaste.',
     'Qué era → cuál fue el reto → qué hiciste tú → resultado con números si puedes.',
     "I worked on migrating our database to a new system without downtime. The hard part was keeping data "
     "consistent. I wrote the migration scripts and a rollback plan, and we finished with zero downtime.",
     'The challenge was|My role was|I was responsible for|We finished with'),
    ('entrevista', 'How do you handle tight deadlines?', '¿Cómo manejas fechas límite ajustadas?',
     'Priorizar → comunicar pronto → pedir ayuda o recortar alcance.',
     "First, I prioritize the most important tasks. If I think we will be late, I tell the team early and we "
     "decide together what to reduce. I prefer to say it early than to surprise everyone.",
     'First, I|I communicate early|We decide together|reduce the scope'),
    ('entrevista', 'What are your salary expectations?', '¿Cuáles son tus expectativas salariales?',
     'Un rango basado en el mercado → apertura a conversar el paquete completo.',
     "Based on my experience and the market, I am looking for a range between X and Y. "
     "I am also open to talking about the full package, including benefits.",
     'Based on my experience|a range between|I am open to discussing'),
    ('entrevista', 'Do you have any questions for us?', '¿Tienes preguntas para nosotros?',
     'Siempre haz 2 preguntas: sobre el equipo y sobre el trabajo diario.',
     "Yes. How is the team organized, and how do you handle code reviews? "
     "Also, what does success look like in the first three months?",
     'How is the team organized|What does a typical day look like|What are the next steps'),
    ('entrevista', 'How do you handle feedback?', '¿Cómo manejas la retroalimentación?',
     'Escuchar → agradecer → actuar → pedir seguimiento.',
     "I try to listen first and ask questions if something is not clear. I thank the person, I make the "
     "changes, and sometimes I ask for feedback again later to check my progress.",
     'I try to listen|I appreciate|I ask for feedback|to check my progress'),
    ('entrevista', 'Tell me about a time you helped a teammate.', 'Cuéntame de una vez que ayudaste a un compañero.',
     'Necesidad del compañero → qué hiciste → resultado para el equipo.',
     "A new teammate was struggling with our deployment process. I prepared a short guide and we did a pair "
     "programming session. After that, she was able to deploy by herself.",
     'was struggling with|I prepared|we did a session|was able to'),
    # ------------------------------------------------------------ técnicas
    ('tecnica', 'Explain what an API is to a non-technical person.',
     'Explica qué es una API a una persona no técnica.',
     'Una analogía simple → un ejemplo cotidiano → una frase de cierre.',
     "An API is like a waiter in a restaurant. You tell the waiter what you want, the waiter talks to the "
     "kitchen, and then brings your food. In the same way, an API takes a request from one program and "
     "returns the answer from another.",
     'It is like|In other words|For example|In the same way'),
    ('tecnica', 'How do you debug a problem in production?', '¿Cómo depuras un problema en producción?',
     'Reproducir → mirar logs y métricas → hipótesis → arreglo seguro → postmortem.',
     "First, I check the logs and the monitoring dashboards to understand what changed. Then I try to "
     "reproduce the problem in a safe environment. If it is urgent, I do a rollback first and look for the "
     "root cause afterwards.",
     'First, I check|I try to reproduce|root cause|rollback'),
    ('tecnica', 'Describe your favorite project and your role in it.', 'Describe tu proyecto favorito y tu rol.',
     'Qué hace el proyecto → tu parte → tecnologías → qué aprendiste.',
     "My favorite project is a booking system I built with Python and PostgreSQL. I designed the database and "
     "wrote the API. I liked it because I could see real users using it every day.",
     'I built|I was responsible for|I used|I liked it because'),
    ('tecnica', 'What is the difference between frontend and backend?',
     '¿Cuál es la diferencia entre frontend y backend?',
     'Definir cada uno en una frase → cómo se comunican.',
     "The frontend is what the user sees and clicks in the browser. The backend runs on the server, handles "
     "the data and the business rules, and talks to the database. They communicate through an API.",
     'is what the user sees|runs on the server|They communicate through'),
    ('tecnica', 'How do you review a pull request?', '¿Cómo revisas un pull request?',
     'Entender el objetivo → leer el diff → probar → comentar con respeto.',
     "First, I read the description to understand the goal. Then I read the changes, I run the code if "
     "needed, and I leave comments. I try to be kind and to explain why I suggest a change.",
     'First, I read|I leave comments|I suggest|I try to be kind'),
    ('tecnica', 'Explain a technical decision you made and why.', 'Explica una decisión técnica que tomaste y por qué.',
     'Opciones → criterios → decisión → resultado.',
     "We had to choose between building our own queue system and using a managed one. I compared the cost, the "
     "time, and the risk, and I recommended the managed service. It saved us about two months of work.",
     'We had to choose between|I compared|I recommended|It saved us'),
    ('tecnica', 'How do you keep your technical skills up to date?', '¿Cómo mantienes tus habilidades técnicas al día?',
     'Hábitos concretos: lectura, proyectos, comunidad.',
     "I read technical blogs and documentation every week, and I build small side projects to try new tools. "
     "I also watch conference talks when I have time.",
     'I read|I build side projects|I watch talks|I try new tools'),
    ('tecnica', 'What happens when you type a URL in the browser?',
     '¿Qué pasa cuando escribes una URL en el navegador?',
     'Paso a paso: DNS → conexión → petición → respuesta → renderizado.',
     "First, the browser asks a DNS server for the IP address. Then it opens a connection to the server and "
     "sends an HTTP request. The server sends back a response, and the browser renders the page.",
     'First|Then|sends back|Finally'),
    ('tecnica', 'How do you test your code?', '¿Cómo pruebas tu código?',
     'Tipos de pruebas → cuándo las corres → qué haces con los fallos.',
     "I write unit tests for the main logic and a few integration tests for the important flows. "
     "I run them locally before pushing, and the pipeline runs them again on every pull request.",
     'I write unit tests|integration tests|before pushing|on every pull request'),
    # ------------------------------------------------------------ reuniones
    ('reunion', 'Give your daily standup update.', 'Da tu actualización del standup.',
     'Ayer → hoy → bloqueos. Tres frases cortas.',
     "Yesterday I finished the login endpoint and started the tests. Today I will fix the failing tests and "
     "open a pull request. I am not blocked right now.",
     'Yesterday I|Today I will|I am blocked by|I am not blocked'),
    ('reunion', 'Explain a blocker to your team.', 'Explica un bloqueo a tu equipo.',
     'Qué te bloquea → desde cuándo → qué necesitas y de quién.',
     "I am blocked on the payment integration. I need the API keys from the finance team, and I asked for them "
     "two days ago. Could someone help me contact them?",
     'I am blocked on|I need|I asked for|Could someone help me'),
    ('reunion', 'Ask a teammate for help with a bug.', 'Pide ayuda a un compañero con un error.',
     'Contexto breve → lo que ya intentaste → pregunta concreta.',
     "Hi, do you have a minute? I am getting a timeout error when I call the orders endpoint. I already checked "
     "the logs and the configuration. Could you take a look with me?",
     'Do you have a minute|I am getting|I already tried|Could you take a look'),
    ('reunion', 'Politely disagree with a technical proposal.', 'Muestra desacuerdo con una propuesta técnica, con cortesía.',
     'Reconocer lo bueno → explicar tu preocupación → proponer alternativa.',
     "I see your point, and I like the idea. However, I am worried that this solution will be hard to maintain. "
     "What do you think about a simpler approach?",
     'I see your point|However, I am worried that|What do you think about'),
    ('reunion', 'Explain a delay to your manager.', 'Explica un retraso a tu jefe.',
     'Hechos → causa → nuevo plan → fecha realista.',
     "I want to let you know that the feature will be two days late. We found a problem in the database that we "
     "did not expect. I have a plan to fix it, and I expect to finish on Thursday.",
     'I want to let you know|will be late|I have a plan|I expect to finish'),
    ('reunion', 'Introduce yourself to a new team.', 'Preséntate ante un equipo nuevo.',
     'Nombre y rol → experiencia breve → algo personal → ganas de aprender.',
     "Hi everyone, my name is Alex and I am a backend developer. I have worked mostly with Python. "
     "Outside of work, I like cycling. I am happy to be here and I am excited to learn from you.",
     'my name is|I have worked mostly with|Outside of work|I am excited to'),
]
