import ngk
import main

r=ngk.ResourceFile("yes")
r.load("sounds.dat",2)
ngk.set_global_resource_file(r)

if __name__=="__main__": main.main()
