from fastapi_cache import FastAPICache
from fastapi_cache.backends.memory import InMemoryCacheBackend
from create_app import app

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryCacheBackend())

async def SetProjectCache(projId,licensekey,projobj,version):
    cacheKey=await createCacheKey(projId,licensekey,version)   
    await FastAPICache.get_backend().set(cacheKey, projobj)


async def GetProjectFromCache(projId,licensekey,version):
    cacheKey=await createCacheKey(projId,licensekey,version)
    return await FastAPICache.get_backend().get(cacheKey)

async def ClearProjectCache():
    await FastAPICache.get_backend().flush()
    pass

async def createCacheKey(projId,licensekey,version=""):
    return  f"{projId}.{licensekey}.{version}"


async def SetPolicyDetCache(policyid,policyentity):
    cacheKey=await createCacheKey(policyid,"pol")   
    await FastAPICache.get_backend().set(cacheKey, policyentity)


async def GetPolicyDetFromCache(policyid):
    cacheKey=await createCacheKey(policyid,"pol")
    return await FastAPICache.get_backend().get(cacheKey)