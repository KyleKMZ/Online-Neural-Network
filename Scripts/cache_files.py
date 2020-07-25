def cache_files(files, cache_dir=None, min_free_space_ratio=2):
    if cache_dir is None: return None
    
    import sh, psutil, glob, time
    from pathlib import Path

    pc = Path(cache_dir)
    pc.mkdir(parents=True, exist_ok=True)

    available_disk_space = psutil.disk_usage(cache_dir).free
    total_file_size = 0
    for filename in files:
        total_file_size += os.path.getsize(filename)
    
    if available_disk_space < total_file_size * min_free_space_ratio: # only when there is enough free disk space
        return None
    
    mapping = {}
    todel = set()
    for f in files:
        f1 = Path(f)
        f2 = pc / f1.name
        mapping[f] = f2.as_posix()
        todel.add(f2.as_posix())
        if f2.exists() and f2.stat().st_size == f1.stat().st_size:
            continue
        # check if it is already being rsync'ed by another process
        ftmp = glob.glob(cache_dir + os.sep + "." + f + ".*")
        if len(ftmp)==1:
            time0 = time.time()
            while 1:
                if os.path.exists(ftmp[0]):
                    if time.time()-time0>10*60: # wait for 10 minutes at most
                        break
                    time.sleep(5)
                else:
                    break
        if f2.exists() and f2.stat().st_size == f1.stat().st_size:
            continue             
        logging.info(f"Caching {f1} to {f2}")
        sh.rsync(["-a", f1.as_posix(), f2.as_posix()])
    
    if mapping:
        import atexit
        atexit.register(remove_cached_files, cached_files=todel)
    
    return mapping

def remove_cached_files(cached_files=set()):
    if not cached_files: return
    
    import os, logging, psutil, sh
    sh_logger = logging.getLogger('sh')
    sh_logger.setLevel(logging.CRITICAL)
    
    current_process = psutil.Process()
    children = current_process.children(recursive=True)
    my_pids = [str(p.pid) for p in [current_process] + children]
    
    all_pids = []
    for filename in cached_files:
        try:
            all_pids += sh.fuser(filename).split()
        except:
            pass
    
    other_pids = [pid for pid in all_pids if pid not in my_pids]
    if other_pids:
        logging.info(f"Cached files ({' '.join(cached_files)}) will not be removed as they are used by other processes: {' '.join(other_pids)}")
    else:  # not used by another process
        for filename in cached_files:
            try:
                os.remove(filename)
                logging.info(f"Removing cache file {filename}")
            except:
                pass
