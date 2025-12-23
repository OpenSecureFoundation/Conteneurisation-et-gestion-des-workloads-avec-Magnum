# Conteneurisation et gestion des workloads avec Magnum
Projet de conteneurisation et gestion des workloads avec OpenStack Magnum


# Objectifs:

• Déployer un cluster Kubernetes ou Docker Swarm via Magnum et automatiser sa gestion

• Intégrer Magnum avec Heat pour orchestrer des infrastructures hybrides VM + conteneurs

# NB: README à mettre à jour progressivement par l'équipe.

## pour ce projet nous avons preferer utiliser l'environnement DevStack car nous nous trouvons dans un contexte de développement, de test et d'apprentissage. DevStack n'est pas une distribution pour la production, mais c'est l'outil de référence pour expérimenter les fonctionnalités avancées d'OpenStack.

# Qu'est-ce qu'OpenStack?

OpenStack est une plateforme de cloud computing standard ouverte et gratuite. Il est principalement déployé en tant qu'infrastructure en tant que service dans les clouds publics et privés où des serveurs virtuels et d'autres ressources sont disponibles pour les utilisateurs.

# Qu'est-ce que DevStack?

Devstack est une série de scripts utilisés pour créer rapidement un environnement OpenStack complet. Nous pouvons télécharger la dernière version d'OpenStack à partir de la branche git master. 

Exigences minimales
Avant de commencer, assurez-vous d'avoir les prérequis minimums suivants :
• Une installation fraîche Ubuntu 22.04
• Utilisateur avec des privilèges sudo
• 4 GB RAM
• 2 vCPUs
• Capacité du disque dur de 20 Go
• Connexion Internet tres stable

Avec les exigences minimales satisfaites, nous pouvons maintenant procéder.

## Étape 1: Mettre à jour et mettre à niveau le système

Pour démarrer, connectez-vous à votre système Ubuntu 22.04 à l'aide du protocole SSH et mettez à jour et mettez à niveau les dépôts système à l'aide de la commande suivante : 

```
apt update -y && apt upgrade -y
```

Ensuite, redémarrez le système en utilisant la commande: `sudo reboot` ou `init 6`

## Étape 2: Créez un utilisateur Stack et attribuez un privilège sudo

Les meilleures pratiques exigent que devstack soit exécuté en tant qu'utilisateur régulier avec des privilèges sudo. Dans cet esprit, nous allons ajouter un nouvel utilisateur appelé **stack** et attribuer des privilèges sudo. Pour créer l'exécution de l'utilisateur de pile

```
sudo adduser -s /bin/bash -d /opt/stack -m stack
sudo chmod +x /opt/stack
```

Ensuite, exécutez la commande ci-dessous pour attribuer des privilèges sudo à l'utilisateur
```
echo "stack ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/stack
```
## Étape 3: Installez git et téléchargez DevStack

Une fois que vous avez créé avec succès l’utilisateur **stack** et les privilèges sudo attribués, passez à l’utilisateur en utilisant la commande : 
```
su - stack
```

Dans la plupart des systèmes Ubuntu 22.04, git est déjà installé. Si par hasard git est manquant, installez-le en exécutant la commande suivante.
```
sudo apt install git -y
```

En utilisant git, clonez le dépôt git de devstack : 
```
git clone https://git.openstack.org/openstack-dev/devstack
```
## Étape 4: Créer un fichier de configuration devstack

Dans cette étape, accédez au répertoire devstack : 
```
cd devstack
```

Puis créer un local.conf fichier de configuration :
```
vim local.conf
ou
nona local.conf
```

Coller le contenu suivant: 
```
[[local|local]]
# Mot de passe pour KeyStone, base de données, RabbitMQ et service
ADMIN_PASSWORD=StrongAdminSecret
DATABASE_PASSWORD=$ADMIN_PASSWORD
RABBIT_PASSWORD=$ADMIN_PASSWORD
SERVICE_PASSWORD=$ADMIN_PASSWORD
# Historique IP - obtenir votre adresse IP Serveur/VM à partir de la commande ip addr
HOST_IP=10.208.0.10
```

Enregistrez et quittez l'éditeur de texte. 

### NOTE:
    Le ADMIN_PASSWORD est le mot de passe que vous utiliserez pour vous connecter à la page de connexion OpenStack. Le nom d'utilisateur par défaut est admin. Le HOST_IP est l'adresse IP de votre système qui est obtenue en exécutant ifconfigo u ip addr commandes.

## Étape 5: Installez OpenStack avec Devstack

Pour commencer l'installation d'OpenStack sur Ubuntu 22.04, exécutez le script ci-dessous contenu dans le répertoire devstack.
```
./stack.sh
```

Les caractéristiques suivantes seront installées :

    Horizon — Tableau de bord OpenStack
    Nova — Service de calcul
    Glance — Service d'image
    Neutron — Service de réseau
    Keystone — Service d'identité
    Cinder — Service de stockage de blocs
    Placement — API de placement

Le déploiement prend environ 10 à 15 minutes en fonction de la vitesse de votre système et de votre connexion Internet. Dans notre cas, cela a pris environ 35 minutes. À la toute fin, vous devriez voir les informations de connection a l'interface de connexion a Horizon et a Neutron.

## Étape 6: Accès à OpenStack sur un navigateur web

Pour accéder à OpenStack via un navigateur Web, parcourez l'adresse IP de votre Ubuntu comme indiqué. https://server-ip/dashboard Cela vous dirige vers une page de connexion comme indiqué.

ok, les etapes suivantes consisterons a l'ajouts de **Heat** et **Magnum** dans notre fichier local.conf pour les differentes configurations.
