# 🚀 Task Manager - AWS Multi-Tier Application

[![AWS](https://img.shields.io/badge/AWS-100%25-orange)](https://aws.amazon.com)
[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://python.org)
[![Cost](https://img.shields.io/badge/Cost-0€%2Fmonth-brightgreen)](https://aws.amazon.com/free/)

> **Multi-tier web application deployed on AWS using Infrastructure as Code**
>

## 🏗️ Architecture

```
Internet → Load Balancer → EC2 (Flask App) → Database
                ↓
            S3 (Assets) + Lambda (Notifications)
```

**Services Used:**
- **EC2 t3.micro** - Application hosting (750h/month free)
- **S3** - Static storage (5GB free)  
- **Lambda** - Serverless functions (1M requests/month free)
- **VPC + IAM** - Security and networking
- **CloudFormation** - Infrastructure as Code


## 🚀 Quick Deploy

```bash
# 1. Clone repository
git clone https://github.com/YassineRh-work/task-manager-aws
cd task-manager-aws

# 2. Configure AWS CLI
aws configure

# 3. Deploy infrastructure
aws cloudformation create-stack \
  --stack-name task-manager-dev \
  --template-body file://infrastructure/final-working.yaml \
  --capabilities CAPABILITY_NAMED_IAM

# 4. Get application URL
aws cloudformation describe-stacks \
  --stack-name task-manager-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue' \
  --output text
```

## 📁 Project Structure

```
task-manager-aws/
├── app/                    # Flask application
│   ├── app.py             # Main application
│   └── requirements.txt   # Python dependencies
├── infrastructure/        # CloudFormation templates
│   └── final-working.yaml         # Infrastructure definition
├── .github/workflows/     # CI/CD pipelines
└── scripts/              # Deployment scripts
```

## 🔄 CI/CD Pipeline

**GitHub Actions** automatically:
- ✅ Tests code quality and security
- ✅ Validates CloudFormation templates  
- ✅ Deploys to AWS on push to `main`
- ✅ Runs integration tests
- ✅ Sends notifications

## 🧪 Local Development

```bash
# Install dependencies
pip install -r app/requirements.txt

# Run locally
cd app && python app.py

# Access at http://localhost:5000
```

## 🔒 Security Features

- **IAM Roles** with least privilege
- **VPC** network isolation
- **Security Groups** application firewall
- **No hardcoded credentials**

## 📊 Features

### Web Interface
- Modern responsive design
- Task creation and management
- Real-time statistics
- AWS architecture overview

### API Endpoints
```bash
GET  /                 # Web interface
GET  /health          # Health check
GET  /api/tasks       # List tasks
POST /api/tasks       # Create task
PUT  /api/tasks/{id}  # Update task
```

### AWS Integration
- **S3 file uploads** with pre-signed URLs
- **Lambda notifications** on task events
- **CloudWatch monitoring** and health checks

## 🎯 Key Points

**Key Technical Points:**
1. **Infrastructure as Code** - Complete AWS stack in CloudFormation
2. **Multi-Service Architecture** - EC2, S3, Lambda, VPC, IAM integration
3. **Cost Optimization** - 0€/month using Free Tier efficiently
4. **DevOps Pipeline** - Automated testing, deployment, and monitoring
5. **Security Best Practices** - IAM, VPC, least privilege access

**Demo Ready:**
- Live application with web interface
- Real AWS infrastructure deployed
- Working CI/CD pipeline
- Complete source code walkthrough

## 🚀 Deployment Environments

| Environment | Stack Name | Purpose |
|-------------|------------|---------|
| Development | `task-manager-dev` | Feature development |
| Production | `task-manager-prod` | Live environment |

## 📞 Contact

**[Yassine Rhourri]** - [yassinerhourri@gmail.com]

Project: [https://github.com/YassineRh-work/task-manager-aws]

---
