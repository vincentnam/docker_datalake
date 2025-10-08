#!/bin/bash
set -x
#sudo docker swarm leave --force
#yes | sudo docker  system prune -a
# Exécuter la commande initiale et capturer la sortie (stderr et stdout)
#output=$(sudo docker swarm init 2>&1)

echo $output
#
## Vérifier si l'erreur spécifique est présente
#if echo "$output" | grep -q "could not choose an IP address to advertise since this system has multiple addresses on different interfaces"; then
#    # Extraire le contenu entre parenthèses
#    inside=$(echo "$output" | sed -n 's/.*(\(.*\)).*/\1/p')
#
#    # Découper en parties séparées par " and "
#    temp="${inside// and /|}"
#    IFS='|' read -ra parts <<< "$temp"
#
#    # Parcourir les parties pour identifier l'IP non-loopback
#    advertise_ip=""
#    for part in "${parts[@]}"; do
#        # Extraire l'IP (avant " on ")
#        ip=$(echo "$part" | sed 's/^\(.*\) on .*/\1/')
#        # Extraire l'interface (après " on ")
#        iface=$(echo "$part" | sed 's/.* on \(.*\)$/\1/')
#
#        # Si ce n'est pas "lo", c'est l'IP à utiliser
#        echo $iface
#        if [[ "$iface" != "lo" ]]; then
#            advertise_ip="$ip"
#            break
#        fi
#    done
#
#    if [[ -n "$advertise_ip" ]]; then
#        echo "Adresse IP détectée pour --advertise-addr : $advertise_ip"
#        # Relancer la commande avec l'adresse
#        sudo docker swarm init --advertise-addr "$advertise_ip" 2>&1 | tee dockerswarm_token.md
#
#    else
#        echo "Impossible d'extraire l'adresse IP non-loopback."
#        echo "Sortie originale : $output"
#    fi
#else
#    echo "Aucune erreur de ce type. Swarm initialisé avec succès."
#    echo "Sortie : $output"
#fi
#




sudo  rm -rf conf scripts/account scripts/objects scripts/container scripts/proxy
mkdir -p conf/account conf/object conf/container conf/proxy
mkdir -p scripts/storage scripts/management
mkdir -p rsyncd
#
rm scripts/config_cluster.env
cp config_cluster.env scripts/config_cluster.env
#
#
#
./create_docker.sh



#
#
#sudo docker stack deploy -c docker-compose_cluster.yml swift_cluster
sudo docker compose -f docker-compose_cluster.yml up --build
