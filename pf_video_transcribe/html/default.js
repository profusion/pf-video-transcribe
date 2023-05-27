function createTimeActiveTracker(videoEl, className) {
    function getStart(element) {
        const { dataset: { start } } = element;
        if (start === undefined) {
            if (element.parentNode) {
                return getStart(element.parentNode);
            }
        }
        return start;
    }

    function seek(clickEvent) {
        clickEvent.preventDefault();
        const start = getStart(clickEvent.target)
        if (start == undefined) {
            console.warn("missing dataset.start:", clickEvent);
            return;
        }
        console.log("seek to:", className, start);
        videoEl.currentTime = start;
    }

    const array = [];
    for (const element of document.getElementsByClassName(className)) {
        const start = Number(element.dataset.start);
        const end = Number(element.dataset.end);
        array.push({ start, end, element });
        element.onclick = seek;
    }

    let currentIdx;

    function findTime(time, backwards) {
        const start = currentIdx || 0;
        if (backwards) {
            for (let i = start; i >= 0; i--) {
                const { start, end } = array[i];
                if (start <= time && time <= end) {
                    return [i, true];
                }
                if (time > end) {
                    return [i, false];
                }
            }
        } else {
            for (let i = start; i < array.length; i++) {
                const { start, end } = array[i];
                if (start <= time && time <= end) {
                    return [i, true];
                }
                if (time < start) {
                    return [i, false];
                }
            }
        }
        return [0, false];
    }

    return function update(time) {
        let backwards = false;
        if (currentIdx !== undefined) {
            backwards = time < array[currentIdx].start;
        }
        const [i, found] = findTime(time, backwards);
        if (i === currentIdx || !found) {
            if (currentIdx !== undefined) {
                return array[currentIdx].element;
            }
            return undefined;
        }
        if (currentIdx !== undefined) {
            const oldEl = array[currentIdx].element;
            oldEl.classList.remove("active");
        }
        const newEl = array[i].element;
        newEl.classList.add("active");
        currentIdx = i;
        return newEl;
    };
}

function createGoToCurrentTracker() {
    let currentEl;

    const viewportEl = document.getElementById("transcription");

    const goToCurrentButton = document.createElement("button");
    goToCurrentButton.id = "go-to-current";
    goToCurrentButton.textContent = "Focus Current Time";
    goToCurrentButton.onclick = function goToCurrent() {
        if (currentEl) {
            console.log("focus current time:", currentEl);
            currentEl.scrollIntoView({ behavior: "smooth", block: "center" });
        }
    };
    viewportEl.insertBefore(goToCurrentButton, viewportEl.firstChild);

    function onIntersection(entries) {
      entries.forEach(entry => {
        goToCurrentButton.classList.toggle("visible", !entry.isIntersecting);
      });
    }

    const observer = new IntersectionObserver(onIntersection, {
      root: viewportEl,
      threshold: 0.5,
    });

    return function update(el) {
        if (currentEl === el) {
            return;
        }
        if (currentEl) {
            observer.unobserve(currentEl);
        }
        currentEl = el;
        if (currentEl) {
            observer.observe(currentEl);
        }
    };
}

function onLoad() {
    const videoEl = document.getElementById("viewer");
    videoEl.autoplay = true;
    videoEl.controls = true;
    videoEl.preload = "auto";

    const goToCurrentTracker = createGoToCurrentTracker();

    const segmentsTracker = createTimeActiveTracker(videoEl, "segment");
    const wordsTracker = createTimeActiveTracker(videoEl, "word");

    videoEl.ontimeupdate = () => {
        const time = videoEl.currentTime;
        segmentsTracker(time);
        goToCurrentTracker(wordsTracker(time));
    };
}

window.addEventListener("DOMContentLoaded", onLoad);
