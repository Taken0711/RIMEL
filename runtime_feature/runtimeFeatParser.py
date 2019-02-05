import json
import sys
from subprocess import Popen, PIPE, call


def gitcheckout(commitHash):
    print("checking out commit " + commitHash,file=sys.stderr)
    call(['git','checkout',commitHash])
    print("checked out " + commitHash,file=sys.stderr)

def getCommitDate(commitHash):
    p = Popen(['git','show','-s','--format=%ci',commitHash],stdout=PIPE)
    out = p.communicate()[0]
    return out.decode("utf-8").replace('\n','')

gitLogFile = open('../RIMEL/runtime_feature/commitList.txt','r')
gitlog = gitLogFile.readlines()
gitLogFile.close()
filePath = './third_party/blink/renderer/platform/runtime_enabled_features.json5'
max = 413
changeLog = []

for i in range(max) : 
    commit = gitlog[i].replace('\n','')
    currentCommit = dict()
    currentCommit['commit'] = commit
    currentCommit['date'] = getCommitDate(commit)
    gitcheckout(commit)

    features = []
    
    featureFile = open(filePath,'r')
    fileContent = featureFile.read()

    p = Popen(['json5', filePath],stdout=PIPE)
    out = p.communicate()[0]

    featureArray = json.loads(out)['data']
    featureFile.close()
    
    test = 0
    experimental = 0
    stable = 0
    missing = 0
    for feat in featureArray : 
        elem = dict()
        elem['name'] = feat['name']
        if 'status' in feat :
            elem['status'] = feat['status']
            if feat['status'] == 'test' :
                test+=1
            elif feat['status'] == 'experimental':
                experimental+=1
            elif feat['status'] == 'stable':
                stable +=1
        else :
            missing +=1
            elem['status'] = 'nowhere'

        features.append(elem)
    
    currentCommit['nbTest'] = test
    currentCommit['nbExperimental'] = experimental
    currentCommit['nbStable'] = stable
    currentCommit['nbMissing'] = missing

    currentCommit['features'] = features

    changeLog.append(currentCommit)

    

print(json.dumps(changeLog))


