# MagnumDash — Interface de Gestion OpenStack Magnum + Heat

Interface web Python/Flask pour la gestion complète de clusters Kubernetes/Docker Swarm
via OpenStack Magnum, avec orchestration hybride Heat et monitoring intégré.

---

## Fonctionnalités

- **Clusters Magnum** — Créer, lister, supprimer des clusters Kubernetes/Swarm
- **Scaling** — Mise à l'échelle manuelle des worker nodes via l'API Magnum
- **Cluster Templates** — Créer et gérer les templates de clusters réutilisables
- **Stacks Heat Hybrides** — Déployer des stacks combinant VMs Nova + Clusters Magnum
- **Monitoring** — Quotas Nova, instances, alarmes Aodh, réseaux Neutron, images Glance
- **Kubeconfig** — Récupération des credentials des clusters

---

## Architecture

```
magnum-dashboard/
├── app.py                  # Point d'entrée Flask
├── requirements.txt
├── .env.example            # Template de configuration
├── services/
│   ├── openstack_client.py # Connexion openstacksdk
│   ├── magnum_service.py   # Gestion clusters & templates
│   ├── heat_service.py     # Stacks hybrides
│   └── monitoring_service.py # Métriques, alarmes, ressources
├── routes/
│   ├── clusters.py         # API /api/clusters/
│   ├── templates.py        # API /api/templates/
│   ├── stacks.py           # API /api/stacks/
│   └── monitoring.py       # API /api/monitoring/
└── templates/
    ├── base.html           # Layout commun (sidebar, topbar)
    ├── index.html          # Dashboard principal
    ├── clusters.html       # Gestion des clusters
    ├── cluster_templates.html
    ├── stacks.html         # Stacks Heat hybrides
    └── monitoring.html     # Monitoring & alarmes
```

---

## Installation

### 1. Pré-requis

- Python 3.10+
- OpenStack opérationnel avec les services : Magnum, Heat, Nova, Neutron, Glance, Keystone, Aodh, Gnocchi
- Accès réseau au Controller OpenStack depuis la machine hôte

### 2. Cloner / copier le projet

```bash
# Sur votre serveur ou sur le Controller OpenStack
cd /opt
git clone <votre-repo> magnum-dashboard
cd magnum-dashboard
```

### 3. Environnement virtuel Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configuration

```bash
cp .env.example .env
nano .env
```

Remplissez les valeurs :
```env
OS_AUTH_URL=http://<CONTROLLER_IP>:5000/v3
OS_PROJECT_NAME=admin
OS_USERNAME=admin
OS_PASSWORD=<votre_mot_de_passe>
OS_USER_DOMAIN_NAME=Default
OS_PROJECT_DOMAIN_NAME=Default
OS_REGION_NAME=RegionOne
```

> **Astuce** : Ces valeurs correspondent exactement aux variables du fichier `admin-openrc.sh`
> que vous pouvez source-r depuis votre Controller : `source /etc/openstack/admin-openrc.sh`

### 5. Lancer l'application

```bash
source venv/bin/activate
python app.py
```

L'interface sera accessible sur : **http://0.0.0.0:5000**

---

## Déploiement en production

### Avec Gunicorn (recommandé)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Service systemd

```ini
# /etc/systemd/system/magnum-dash.service
[Unit]
Description=MagnumDash - OpenStack Magnum Dashboard
After=network.target

[Service]
Type=simple
User=djanze
WorkingDirectory=/opt/magnum-dashboard
EnvironmentFile=/opt/magnum-dashboard/.env
ExecStart=/opt/magnum-dashboard/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable magnum-dash
sudo systemctl start magnum-dash
sudo systemctl status magnum-dash
```

---

## Routes API disponibles

### Clusters
| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/clusters/` | Lister tous les clusters |
| POST | `/api/clusters/` | Créer un cluster |
| GET | `/api/clusters/<id>` | Détail d'un cluster |
| DELETE | `/api/clusters/<id>` | Supprimer un cluster |
| POST | `/api/clusters/<id>/scale` | Scaler (body: `{"node_count": N}`) |
| GET | `/api/clusters/<id>/config` | Récupérer le kubeconfig |

### Cluster Templates
| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/templates/` | Lister les templates |
| POST | `/api/templates/` | Créer un template |
| GET | `/api/templates/<id>` | Détail d'un template |
| DELETE | `/api/templates/<id>` | Supprimer un template |

### Stacks Heat
| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/stacks/` | Lister les stacks |
| POST | `/api/stacks/hybrid` | Créer une stack hybride VM+Cluster |
| POST | `/api/stacks/custom` | Créer une stack depuis un template HOT |
| DELETE | `/api/stacks/<id>` | Supprimer une stack |
| GET | `/api/stacks/<id>/resources` | Ressources d'une stack |
| GET | `/api/stacks/<id>/events` | Événements d'une stack |
| GET | `/api/stacks/template/hybrid` | Template HOT hybride de référence |

### Monitoring
| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/monitoring/summary` | Résumé global (clusters, stacks, VMs) |
| GET | `/api/monitoring/compute` | Quotas Nova (vCPU, RAM, instances) |
| GET | `/api/monitoring/alarms` | Alarmes Aodh |
| POST | `/api/monitoring/alarms` | Créer une alarme |
| DELETE | `/api/monitoring/alarms/<id>` | Supprimer une alarme |
| GET | `/api/monitoring/servers` | Liste des instances Nova |
| GET | `/api/monitoring/resources/keypairs` | Keypairs disponibles |
| GET | `/api/monitoring/resources/flavors` | Flavors disponibles |
| GET | `/api/monitoring/resources/networks` | Réseaux Neutron |
| GET | `/api/monitoring/resources/images` | Images Glance |

---

## Troubleshooting

**Erreur de connexion OpenStack :**
```bash
# Vérifier la connectivité au Keystone
curl http://<CONTROLLER_IP>:5000/v3
# Tester les credentials
openstack --os-auth-url http://<CONTROLLER_IP>:5000/v3 \
          --os-username admin --os-password <pass> \
          --os-project-name admin token issue
```

**openstacksdk non trouvé :**
```bash
source venv/bin/activate
pip install openstacksdk
```

**Port 5000 déjà utilisé :**
```bash
# Changer le port dans .env
FLASK_PORT=8080
```

---

## Auteurs

- ESSONO EFFA Etienne Florian
- NGNINTEDEM FEUPI Vaillant

Sous la supervision de M. NGUIMBUS Emmanuel
Université Saint Jean — Année Académique 2025-2026
