apt update
apt upgrade
apt install git bdf2psf otf2bdf gcc g++ python3 python3-dev python3-twisted pyton3-setuptools python3-wheel python3-opencv python3-numpy python3-pip python3-pillow libgraphicsmagick++1-dev libwebp-dev cmake avahi-daemon libavahi-client3 ffmpeg vim fonts-powerline zsh -y
pip install Pillow RPi.GPIO bdist_wheel
git clone --recursive https://github.com/buresu/ndi-python.git
systemctl enable --now avahi-daemon
./InstallNDISDK.sh
env CMAKE_ARGS="/root/ndilinux" python3 setup.py bdist_wheel
