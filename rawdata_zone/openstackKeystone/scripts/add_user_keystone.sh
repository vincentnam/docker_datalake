#!/bin/bash

# =============================================
# add_user_with_project.sh
# =============================================
# Usage : ./add_user_with_project.sh <username>
# Exemple : ./add_user_with_project.sh vincent

if [ $# -eq 0 ]; then
  echo "Usage: $0 <username> <password>"
  echo "Exemple: $0 alice toto"
  exit 1
fi

USERNAME="$1"
PROJECT="$USERNAME"
PASSWORD="$2"
ROLE="bucket_owner"


export OS_USERNAME=admin
export OS_PASSWORD=Camion_Rapide_Sable_Jaune_Boulot_99
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_AUTH_URL=http://localhost:5000/v3
export OS_IDENTITY_API_VERSION=3
# Fonctions de création idempotentes (copiées/adaptées de ton bootstrap)








openstack user create --domain Default --password "$user_password" "$user_name"
openstack project create --domain Default --description "Projet utilisateur $project_name" "$project_name"
openstack role add --project "$PROJECT" --user "$USERNAME" "$ROLE"
openstack role assignment list --user "$USERNAME" --project "$PROJECT" --names

echo "Attribution du rôle $ROLE à $USERNAME sur le projet $PROJECT"
# Vérifications finales
echo
echo "Opération terminée !"
echo "Utilisateur : $USERNAME"
echo "Projet     : $PROJECT"
echo "Mot de passe : $PASSWORD"
echo "Rôle       : $ROLE"
echo
echo "Vérification rapide :"
openstack user show "$USERNAME"
openstack project show "$PROJECT"
