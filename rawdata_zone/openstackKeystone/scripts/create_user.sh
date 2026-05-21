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

# Keystone admin credentials (identiques à ton bootstrap)
: "${OS_AUTH_URL:=http://localhost:5000/v3}"
: "${OS_USERNAME:=admin}"
: "${OS_PASSWORD:=Camion_Rapide_Sable_Jaune_Boulot_99}"
: "${OS_PROJECT_NAME:=admin}"
: "${OS_USER_DOMAIN_NAME:=Default}"
: "${OS_PROJECT_DOMAIN_NAME:=Default}"

# Fonctions de création idempotentes (copiées/adaptées de ton bootstrap)
ensure_role() {
    local role_name="$1"
    if ! openstack role show "$role_name" >/dev/null 2>&1; then
        echo "→ Création du rôle : $role_name"
        openstack role create "$role_name" >/dev/null
    fi
}

ensure_project() {
    local project_name="$1"
    if ! openstack project show "$project_name" >/dev/null 2>&1; then
        echo "→ Création du projet : $project_name"
        openstack project create --domain Default --description "Projet utilisateur $project_name" "$project_name" >/dev/null
    fi
}

ensure_user() {
    local user_name="$1"
    local user_password="$2"
    if ! openstack user show "$user_name" >/dev/null 2>&1; then
        echo "→ Création de l'utilisateur : $user_name"
        openstack user create --domain Default --password "$user_password" "$user_name" >/dev/null
    else
        echo "→ Utilisateur $user_name existe déjà (mot de passe inchangé)"
    fi
}

# Attente de Keystone (comme dans ton bootstrap)
echo "Attente de Keystone..."
until openstack token issue >/dev/null 2>&1; do
    echo "Keystone indisponible, nouvelle tentative dans 5s..."
    sleep 5
done
echo "Keystone prêt."

# Création
ensure_role "$ROLE"
ensure_project "$PROJECT"
ensure_user "$USERNAME" "$PASSWORD"

echo "Attribution du rôle $ROLE à $USERNAME sur le projet $PROJECT"
openstack role add --project "$PROJECT" --user "$USERNAME" "$ROLE" || true

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
openstack role assignment list --user "$USERNAME" --project "$PROJECT" --names
