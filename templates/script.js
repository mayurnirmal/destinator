// Initialize Lenis
const lenis = new Lenis();

// Use requestAnimationFrame to continuously update the scroll
function raf(time) {
  lenis.raf(time);
  requestAnimationFrame(raf);
}

requestAnimationFrame(raf);

gsap.from(".rotate-div",{
    x:500 ,
    y:100,
    duration:3,
    repeat: -1, yoyo: true
})

var tl=gsap.timeline({scrollTrigger:{
    trigger:".part1",
    start:"50% 50%",
    end:"150% bottom",
    scrub:true,
    // markers:true,    
    pin:true     

}})

tl.to(".rotate-div",{
    rotate:-30,
    scale:0.7
},'a')
tl.to("#row-div-1",{
    marginTop:"-30%",
    opacity:0
},'a')
tl.to("#row-div-2",{
    marginTop:"-30%",
    opacity:0
},'a')
tl.to("#row-div-3",{
    marginTop:"-50%"
},'a')
tl.to("#row-div-4",{
    marginTop:"-20%"
},'a')
tl.to("#row-div-5",{
    marginTop:"-35%"
},'a')

tl.to('.overlay-div',{
    backgroundColor:"black"
},'a')
tl.to('.overlay-div h1',{
    opacity:1
},'a')
tl.to('.scrolling',{
    width:"7vw"
},'a')



// -------text-animation---------
var tl2 = gsap.timeline({scrollTrigger:{
    trigger: ".part-2",
    start:"0% 70%",
    end:"50% 50%",
    scrub:true,
    // markers:true,
}})

tl2.to(".rounded-div-wrapper",{
    height:0,
    marginTop: 0
})


let tl3 = gsap.timeline({
    scrollTrigger:{
        trigger: ".content-2",
        start:"20% 50%",
        end: "100% 50%",
        // markers: true,
        scrub: 1,
    },  
});
tl3.to(".content-2 .text-area-hover h1",{
    width:"100%",
})
tl3.to(".content-2 .text-area-hover h2",{
    delay: -0.4,
    width:"100%",
})
let tl4 = gsap.timeline({
    scrollTrigger:{
        trigger: ".part-4",
        start:"50% 50%",
        end: "200% 50%",
        pin: true,
        // markers: true,
        scrub: 1,
    },  
});
tl4.to(".c-one",{
    marginTop: "-25%",
    opacity:"1",
}, 'sct-1')
tl4.to(".c-two",{
    opacity:"1",
}, 'sct-2')
tl4.to(".c-one",{
    marginTop: "-100",
    opacity:"0",
}, 'sct-2')
tl4.to(".c-three",{
    opacity:"1",
}, 'sct-3')
tl4.to(".c-two",{
    opacity:"0",
}, 'sct-3')
tl4.to(".c-one",{
    marginTop:"-180%",
}, 'sct-3')
tl4.to(".c-one",{
    marginTop:"-230%",
}, 'sct-4')
tl4.to(".c-three",{
    opacity:"0",
}, 'sct-4')
tl4.to(".cir-part-4",{
    marginLeft:"100%",
    rotate: 360
}, 'sct-4')


let tl5 = gsap.timeline({
    scrollTrigger:{
        trigger: ".part-5",
        start:"20% 50%",
        end: "100% 50%",
        // markers: true,
        scrub: 1,
    },  
});
tl5.to(".part-5 .text-area-hover h1",{
    width:"100%",
})
tl5.to(".part-5 .text-area-hover h3",{
    width:"100%",
})
tl5.to(".part-5 .text-area-hover h2",{
    delay: -0.4,
    width:"100%",
})
tl5.to(".part-5 .text-area-hover h3",{
    delay: -0.4,
    width:"100%",
})


let tl6 = gsap.timeline({
    scrollTrigger:{
        trigger: ".part-6",
        start:"0% 70%",
        end: "15% 50%",
        // markers: true,
        scrub: 1,
    },  
});
tl6.to(".rounded-div-wrapper-6",{
    height:"0%",
    marginTop: 0,
})

let tl7 = gsap.timeline({
    scrollTrigger:{
        trigger: ".part-7",
        start:"50% 50%",
        end: "300% 50%",
        pin:true,
        // markers: true,
        scrub: 1,
    },  
});
tl7.to("#demo",{
    bottom:"7%",
})
tl7.to(".our-work-txt-div",{
    height:"60vh",
}, 'height')
tl7.to(".our-work-txt",{
    height:"60vh",
}, 'height')
tl7.to("#our",{
    left:"0%",
}, 'height')
tl7.to("#work",{
    right:"0%",
}, 'height')
tl7.to(".scroll-img",{
    marginTop:"-300%",
})

function loading() {
    let tl = gsap.timeline();
    tl.to("#yellow", {
        top: "-100%",
        delay: 0.5,
        duration: 0.5,
        esae: "expo.out"
    })
    // tl.to("#loader video",{
    //     top:"-100%",
    //     delay:0.5,
    //     duration:0.5,
    //     esae:"expo.out"
    // })
    tl.to("#loader #img14", {
        top: "-100%",
        opacity: 0,
        // delay:0.5,
        duration: 0.1,
        esae: "expo.out"
    })
    tl.to("#loader #img13", {
        left: "-100%",
        opacity: 0,
        // delay:0.5,
        duration: 0.1,
        esae: "expo.out"
    })
    tl.to("#loader #img12", {
        bottom: "-100%",
        opacity: 0,
        // delay:0.5,
        duration: 0.1,
        esae: "expo.out"
    })
    tl.to("#loader #img11", {
        right: "-100%",
        opacity: 0,
        // delay:0.5,
        duration: 0.1,
        esae: "expo.out"
    })
    tl.to("#loader #img10", {
        top: "-100%",
        opacity: 0,
        // delay:0.5,
        duration: 0.1,
        esae: "expo.out"
    })
    tl.to("#loader #img9", {
        left: "-100%",
        opacity: 0,
        // delay:0.5,
        duration: 0.1,
        esae: "expo.out"
    })
    tl.to("#loader #img8", {
        bottom: "-100%",
        opacity: 0,
        // delay:0.5,
        duration: 0.1,
        esae: "expo.out"
    })
    tl.to("#loader #img7", {
        right: "-100%",
        opacity: 0,
        // delay:0.5,
        duration: 0.1,
        esae: "expo.out"
    })
    tl.to("#loader #img6", {
        top: "-100%",
        opacity: 0,
        // delay:0.5,
        duration: 0.1,
        esae: "expo.out"
    })
    tl.to("#loader #img5", {
        left: "-100%",
        opacity: 0,
        // delay:0.5,
        duration: 0.1,
        esae: "expo.out"
    })
    tl.to("#loader #img4", {
        bottom: "-100%",
        opacity: 0,
        // delay:0.5,
        duration: 0.1,
        esae: "expo.out"
    })
    tl.to("#loader #img3", {
        right: "-100%",
        opacity: 0,
        // delay:0.5,
        duration: 0.1,
        esae: "expo.out"
    })
    tl.to("#loader #img2", {
        top: "-100%",
        opacity: 0,
        // delay:0.5,
        duration: 0.1,
        esae: "expo.out"
    })
    tl.to("#loader #img1", {
        left: "-100%",
        opacity: 0,
        // delay:0.5,
        duration: 0.1,
        esae: "expo.out"
    })
    tl.to("#loader", {
        opacity: 0
    })
    tl.to("#loader", {
        display: "none"
    })
}
loading();