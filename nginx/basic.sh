#!/bin/bash
if [ "${BASIC_USER:+foo}" ] && [ "${BASIC_PASS:+foo}" ]; then
    echo BASIC認証用のキーを作成
    CRYPTPASS=`openssl passwd -crypt ${BASIC_PASS}`
    echo "${BASIC_USER}:${CRYPTPASS}" >> /etc/nginx/.htpasswd
fi
