eval "$(ssh-agent -s)"
ssh-add ~/.ssh/git_acer
git fetch
git pull
