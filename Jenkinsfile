// Declarative pipeline for EquipGo.
// Flow: Checkout -> Test -> Build Images -> Deploy -> Smoke Test
pipeline {
    agent any

    environment {
        COMPOSE_PROJECT_NAME = 'equipgo'
        TAG = "${env.BUILD_NUMBER}"          // images become equipgo/<service>:<build number>
    }

    triggers {
        githubPush()                         // GitHub webhook (needs a public URL, e.g. ngrok)
        pollSCM('H/2 * * * *')               // fallback: check the repo every ~2 minutes
    }

    options {
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '15'))
        timestamps()
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Test') {
            // Runs each module's Dockerfile "test" stage. A failing test fails the
            // build HERE, so Deploy never runs and the live app keeps its old version.
            steps {
                sh 'docker build --target test -t equipgo/inventory-api:test ./inventory-api'
                sh 'docker build --target test -t equipgo/borrow-api:test ./borrow-api'
                sh 'docker build --target test -t equipgo/worker:test ./worker'
            }
        }

        stage('Build Images') {
            steps {
                withCredentials([file(credentialsId: 'equipgo-env', variable: 'ENV_FILE')]) {
                    sh 'cp "$ENV_FILE" .env'
                    sh 'docker compose build'
                }
            }
        }

        stage('Deploy') {
            steps {
                withCredentials([file(credentialsId: 'equipgo-env', variable: 'ENV_FILE')]) {
                    sh 'cp "$ENV_FILE" .env'
                    sh 'docker compose up -d --no-build --remove-orphans'
                }
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                    for i in $(seq 1 12); do
                      if docker compose exec -T proxy wget -qO- http://127.0.0.1/api/inventory/health \
                         && docker compose exec -T proxy wget -qO- http://127.0.0.1/api/borrow/health \
                         && docker compose exec -T proxy wget -qO- http://127.0.0.1/ > /dev/null; then
                        echo "Smoke test passed"; exit 0
                      fi
                      echo "Waiting for services..."; sleep 5
                    done
                    echo "Smoke test failed"; exit 1
                '''
            }
        }
    }

    post {
        success { echo "EquipGo build ${TAG} is live at http://localhost:8080" }
        failure { echo "Build ${TAG} failed. If it failed before Deploy, the previous version is still running. Rollback: TAG=<previous> docker compose -p equipgo up -d --no-build" }
        always  { sh 'rm -f .env' }
    }
}
