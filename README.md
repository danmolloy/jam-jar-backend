# Jam Jar Backend
## Overview
Jam Jar is a full-stack web application that helps musicians track practice sessions, record audio, set goals, and visualize progress through an analytics dashboard.

The backend provides a clean RESTful API, robust authentication and authorization, and integrations with third-party services such as Stripe and AWS SES.

Check out the [Next.js frontend](https://github.com/danmolloy/jam-jar-frontend).

## Features
### Technical Highlights
* Clean RESTful API design with versioned routes
* Authenticate and authorize users with session- and token-based strategies, including role-based access control.
* Process payments securely with Stripe Checkout and webhook handling
* Background email sending via AWS SES

### Technologies
* Framework & Language: Django REST Framework, Python
* Database: PostgreSQL
* Authentication & Authorization: Django (sessions, tokens, role-based access)
* Payments: Stripe (Checkout + Webhooks)
* Email: AWS SES
* Analytics & Monitoring: Sentry
* Deployment: Heroku

## Under Development
* Extended automated test coverage (Django test framework) 
* CI/CD pipelines with GitHub Actions for linting, testing, and deployment
  
## License
Please respect the intellectual property and don't use this code for commercial purposes without permission.

## Credits
Designed and developed by Daniel Molloy.