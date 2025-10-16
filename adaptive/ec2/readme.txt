ipAll()

idParallel()

gp()

getkeys() #upload the host file

runProtocol()




#Fabric 1 commands

ipAll()
c(getIP(), 'install_dependencies')
c(getIP(), 'git_pull')
c(getIP(), 'syncKeys')


c(getIP(), 'runProtocol:N,t,B,v,time')
c(getIP(), 'runProtocol:4,1,10,1,3')